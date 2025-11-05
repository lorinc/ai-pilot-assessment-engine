"""Configuration management for the application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # GCP Configuration
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    
    # Application Configuration
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "src/data"))
    
    # Testing Configuration
    MOCK_LLM: bool = os.getenv("MOCK_LLM", "false").lower() == "true"
    MOCK_FIREBASE: bool = os.getenv("MOCK_FIREBASE", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings are present."""
        if not cls.GCP_PROJECT_ID and not cls.MOCK_LLM:
            raise ValueError(
                "GCP_PROJECT_ID must be set in environment variables. "
                "Set MOCK_LLM=true for testing without GCP."
            )
        
        if not cls.FIREBASE_CREDENTIALS_PATH and not cls.MOCK_FIREBASE:
            raise ValueError(
                "FIREBASE_CREDENTIALS_PATH must be set in environment variables. "
                "Set MOCK_FIREBASE=true for testing without Firebase."
            )
    
    @classmethod
    def get_data_path(cls, relative_path: str) -> Path:
        """Get absolute path to data file."""
        return (cls.DATA_DIR / relative_path).resolve()


# Create global settings instance
settings = Settings()
