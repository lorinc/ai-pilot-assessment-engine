#!/usr/bin/env python3
"""Main CLI entry point for KB enrichment tool."""

import argparse
import logging
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from orchestrator import EnrichmentOrchestrator


def setup_logging(config: dict) -> None:
    """Setup logging configuration.
    
    Args:
        config: Configuration dictionary
    """
    log_config = config.get("logging", {})
    
    # Create formatters and handlers
    formatter = logging.Formatter(log_config.get("format", "%(levelname)s - %(message)s"))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler
    if log_config.get("file"):
        log_file = Path(log_config["file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
    else:
        file_handler = None
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_config.get("level", "INFO"))
    root_logger.addHandler(console_handler)
    if file_handler:
        root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def load_config(config_path: Path, overrides: dict = None) -> dict:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        overrides: Optional configuration overrides
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Apply overrides
    if overrides:
        for key, value in overrides.items():
            if value is not None:
                # Handle nested keys (e.g., "chunking.chunk_size")
                if "." in key:
                    parts = key.split(".")
                    target = config
                    for part in parts[:-1]:
                        target = target.setdefault(part, {})
                    target[parts[-1]] = value
                else:
                    config[key] = value
    
    return config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Knowledge Base Enrichment Tool - Gemini-powered KB scaffolding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all phases in test mode (default)
  python main.py --all
  
  # Run specific phase
  python main.py --phase 0
  
  # Run phase range
  python main.py --phase 1-3
  
  # Run in full mode
  python main.py --all --mode full
  
  # Resume from checkpoint
  python main.py --all --resume
  
  # Clean and restart
  python main.py --all --clean
  
  # Validate final output
  python main.py --validate
        """
    )
    
    # Execution mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--all",
        action="store_true",
        help="Run all phases sequentially"
    )
    mode_group.add_argument(
        "--phase",
        type=str,
        help="Run specific phase or range (e.g., '0', '1-3')"
    )
    mode_group.add_argument(
        "--validate",
        action="store_true",
        help="Validate final knowledge graph"
    )
    
    # Configuration
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--mode",
        choices=["test", "full"],
        help="Override run mode (test or full)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Override inference chunk size"
    )
    
    # Execution options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-run even if phase is completed"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output directory before running"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    # Load configuration
    if not args.config.exists():
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    overrides = {}
    if args.mode:
        overrides["mode"] = args.mode
    if args.chunk_size:
        overrides["chunking.inference_chunk_size"] = args.chunk_size
    
    config = load_config(args.config, overrides)
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    # Dry run mode
    if args.dry_run:
        logger.info("DRY RUN MODE - No actions will be executed")
        logger.info(f"Configuration: {args.config}")
        logger.info(f"Mode: {config['mode']}")
        logger.info(f"Output: {config['paths']['output_dir']}")
        
        if args.all:
            logger.info("Would execute: All phases (0-3)")
        elif args.phase:
            logger.info(f"Would execute: Phase {args.phase}")
        elif args.validate:
            logger.info("Would execute: Validation")
        
        return
    
    # Initialize orchestrator
    try:
        orchestrator = EnrichmentOrchestrator(config)
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        sys.exit(1)
    
    # Clean output if requested
    if args.clean:
        orchestrator.clean_output()
    
    # Execute requested action
    try:
        if args.validate:
            orchestrator.validate_output()
        
        elif args.all:
            start_phase = "0"
            if args.resume and not args.force:
                # Determine where to resume from
                last_completed = orchestrator.checkpoint.state.get("last_completed_phase")
                if last_completed is not None:
                    start_phase = str(int(last_completed) + 1)
                    if int(start_phase) > 3:
                        logger.info("All phases already completed!")
                        orchestrator._print_final_summary()
                        return
                    logger.info(f"Resuming from phase {start_phase}")
            
            orchestrator.run_all(start_phase=start_phase, force=args.force)
        
        elif args.phase:
            orchestrator.run_phases(args.phase, force=args.force)
        
        logger.info("\n✓ Execution completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("\n\nExecution interrupted by user")
        logger.info("Progress has been saved. Use --resume to continue.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"\n✗ Execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
