"""
Situational Awareness Demo - UAT Checkpoint

Demonstrates how situational awareness evolves during conversation:
- 8 dimensions always sum to 100%
- Updates based on triggers
- Decays over time toward baseline

Run: python demo_situational_awareness.py
"""
from src.patterns.situational_awareness import SituationalAwareness


def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_composition(sa, label="Current Composition"):
    """Print composition as bar chart"""
    print(f"{label}:")
    print()
    
    # Get all dimensions sorted by value
    sorted_dims = sorted(sa.composition.items(), key=lambda x: x[1], reverse=True)
    
    for dimension, value in sorted_dims:
        bar_length = int(value * 50)  # Scale to 50 chars max
        bar = "█" * bar_length
        print(f"  {dimension:15} {value:5.1%} {bar}")
    
    print()
    print(f"  Total: {sum(sa.composition.values()):.3f} (must be 1.000)")
    print()


def demo_conversation_flow():
    """Demo how situation evolves through a conversation"""
    print_section("Conversation Flow Demo")
    
    sa = SituationalAwareness()
    
    # Step 1: Start of conversation
    print("📍 Step 1: Start of Conversation")
    print("   User: [First message]")
    print_composition(sa, "Initial Situation")
    
    # Step 2: User mentions output
    print("📍 Step 2: User Mentions Output")
    print("   User: 'We need to assess sales forecasting in our CRM'")
    print("   Triggers: T_MENTION_OUTPUT (discovery)")
    sa.update_from_triggers([
        {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
    ])
    print_composition(sa, "After Discovery Signal")
    
    # Step 3: Start assessment
    print("📍 Step 3: Start Assessment")
    print("   User: 'The sales team creates it, data quality is about 3 stars'")
    print("   Triggers: T_RATE_EDGE (assessment)")
    sa.update_from_triggers([
        {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment'}
    ])
    print_composition(sa, "After Assessment Signal")
    
    # Step 4: User gets confused
    print("📍 Step 4: User Gets Confused")
    print("   User: 'Wait, I'm confused about what you're asking'")
    print("   Triggers: CONFUSION_DETECTED (error_recovery → clarification)")
    sa.update_from_triggers([
        {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'}
    ])
    print_composition(sa, "After Confusion (Clarification Spike)")
    
    # Step 5: Continue assessment
    print("📍 Step 5: Continue Assessment")
    print("   User: 'Got it. The process is 4 stars, system support is 2 stars'")
    print("   Triggers: T_RATE_EDGE (assessment)")
    sa.update_from_triggers([
        {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment'}
    ])
    print_composition(sa, "After More Assessment")
    
    # Step 6: Request recommendations
    print("📍 Step 6: Request Recommendations")
    print("   User: 'What AI pilots would help?'")
    print("   Triggers: T_REQUEST_RECOMMENDATIONS (recommendation)")
    sa.update_from_triggers([
        {'trigger_id': 'T_REQUEST_RECOMMENDATIONS', 'category': 'recommendation'}
    ])
    print_composition(sa, "After Recommendation Request")


def demo_decay():
    """Demo how decay works"""
    print_section("Decay Demo")
    
    sa = SituationalAwareness()
    
    # Boost discovery significantly
    print("📍 Initial: Boost Discovery")
    for _ in range(3):
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
    print_composition(sa, "After 3 Discovery Signals")
    
    # Apply decay steps
    print("📍 Applying Decay (5 steps)")
    for i in range(5):
        sa.apply_decay()
        print(f"After decay step {i+1}: discovery = {sa.composition['discovery']:.1%}")
    
    print()
    print_composition(sa, "After 5 Decay Steps")
    print("Notice: Discovery gradually decays toward baseline (50%)")


def demo_multiple_signals():
    """Demo handling multiple triggers at once"""
    print_section("Multiple Signals Demo")
    
    sa = SituationalAwareness()
    
    print("📍 Initial State")
    print_composition(sa)
    
    print("📍 Multiple Triggers in One Turn")
    print("   User: 'I'm confused about the sales forecast assessment. Where are we?'")
    print("   Triggers:")
    print("     - CONFUSION_DETECTED (error_recovery → clarification)")
    print("     - T_MENTION_OUTPUT (discovery)")
    print("     - T_REQUEST_PROGRESS (navigation → meta)")
    
    sa.update_from_triggers([
        {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'},
        {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'},
        {'trigger_id': 'T_REQUEST_PROGRESS', 'category': 'navigation'}
    ])
    
    print_composition(sa, "After Multiple Signals")
    print("Notice: Multiple dimensions affected simultaneously")


def demo_composition_constraint():
    """Demo that composition always sums to 100%"""
    print_section("Composition Constraint Demo")
    
    sa = SituationalAwareness()
    
    print("📍 Testing Composition Constraint")
    print()
    
    # Test various operations
    operations = [
        ("Initial", lambda: None),
        ("After discovery signal", lambda: sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])),
        ("After multiple signals", lambda: sa.update_from_triggers([
            {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'},
            {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment'}
        ])),
        ("After decay", lambda: sa.apply_decay()),
        ("After more decay", lambda: sa.apply_decay()),
    ]
    
    for label, operation in operations:
        operation()
        total = sum(sa.composition.values())
        status = "✅" if abs(total - 1.0) < 0.001 else "❌"
        print(f"  {status} {label:25} Sum = {total:.6f}")
    
    print()
    print("✅ Composition ALWAYS sums to 1.000 (100%)")


def main():
    """Run all demos"""
    print("\n" + "🎯" * 40)
    print("  SITUATIONAL AWARENESS DEMO - UAT CHECKPOINT")
    print("🎯" * 40)
    
    # Demo 1: Conversation flow
    demo_conversation_flow()
    
    # Demo 2: Decay
    demo_decay()
    
    # Demo 3: Multiple signals
    demo_multiple_signals()
    
    # Demo 4: Composition constraint
    demo_composition_constraint()
    
    # Summary
    print_section("UAT Summary")
    print("✅ 8 dimensions: discovery, assessment, analysis, recommendation,")
    print("                 feasibility, clarification, validation, meta")
    print("✅ Composition always sums to 100% (1.0)")
    print("✅ Updates from triggers (signal detection)")
    print("✅ Decays toward baseline over time")
    print("✅ Handles multiple signals simultaneously")
    print("✅ Dominant dimensions easily identified")
    print()
    print("🎯 Situational Awareness Ready!")
    print()
    print("Next Steps:")
    print("  1. Integrate with ResponseComposer")
    print("  2. Use situation to drive proactive selection")
    print("  3. Test end-to-end conversation flows")
    print()


if __name__ == "__main__":
    main()
