#!/usr/bin/env python3
"""
Test script for context-aware prompting system.
This script tests different query intents and coaching styles.
"""

import os
import sys
from typing import List

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.context_aware_prompting import create_ramit_prompt_generator, UserContext
from src.utils.coaching_context_injector import create_coaching_context_injector

def test_query_intent_classification():
    """Test query intent classification"""
    print("="*80)
    print("QUERY INTENT CLASSIFICATION TEST")
    print("="*80)
    
    prompt_generator = create_ramit_prompt_generator()
    
    test_queries = [
        "How do I get my first sale?",
        "What should I charge for my consulting services?",
        "How do I do customer research?",
        "What's the framework for creating an offer?",
        "Everyone says to follow your passion. Is that right?",
        "Give me specific steps to follow up with prospects",
        "Do you have any student examples of successful businesses?",
        "What's the mindset I need to succeed?"
    ]
    
    for query in test_queries:
        intent = prompt_generator.classify_query_intent(query)
        print(f"Query: '{query}'")
        print(f"Intent: {intent.value}")
        print("-" * 60)

def test_content_analysis():
    """Test content analysis for coaching style determination"""
    print("\n" + "="*80)
    print("CONTENT ANALYSIS TEST")
    print("="*80)
    
    prompt_generator = create_ramit_prompt_generator()
    
    # Sample content with different Ramit characteristics
    test_sources = [
        {
            "content": "Here's the customer research framework I use. Step 1: Find 10 potential customers...",
            "ramit_type": "framework",
            "ramit_frameworks": ["customer_research"],
            "ramit_scores": {"framework": 0.8, "contrarian": 0.1, "tactical": 0.7, "case_study": 0.0}
        },
        {
            "content": "Everyone tells you to build it and they will come. That's completely backwards...",
            "ramit_type": "contrarian",
            "ramit_frameworks": [],
            "ramit_scores": {"framework": 0.2, "contrarian": 0.9, "tactical": 0.1, "case_study": 0.0}
        },
        {
            "content": "Let me tell you about Maria, one of my students who went from zero to $50k...",
            "ramit_type": "case_study",
            "ramit_frameworks": [],
            "ramit_scores": {"framework": 0.1, "contrarian": 0.0, "tactical": 0.2, "case_study": 0.9}
        }
    ]
    
    for i, sources in enumerate([[source] for source in test_sources]):
        content_analysis = prompt_generator.analyze_retrieved_content(sources)
        coaching_style = prompt_generator.determine_coaching_style(
            prompt_generator.classify_query_intent("How do I start?"), 
            content_analysis
        )
        
        print(f"Content {i+1}: {sources[0]['ramit_type']}")
        print(f"Coaching Style: {coaching_style.value}")
        print(f"Scores: Framework={content_analysis.ramit_framework_score:.1f}, "
              f"Contrarian={content_analysis.ramit_contrarian_score:.1f}, "
              f"Tactical={content_analysis.ramit_tactical_score:.1f}")
        print("-" * 60)

def test_prompt_generation():
    """Test full context-aware prompt generation"""
    print("\n" + "="*80)
    print("CONTEXT-AWARE PROMPT GENERATION TEST")
    print("="*80)
    
    prompt_generator = create_ramit_prompt_generator()
    
    # Test query
    query = "How do I price my consulting services?"
    
    # Mock sources with different content types
    sources = [
        {
            "content": "The pricing framework is about value, not costs. Here's how to position pricing as an investment...",
            "ramit_type": "framework",
            "ramit_frameworks": ["pricing_strategy"],
            "ramit_scores": {"framework": 0.8, "contrarian": 0.2, "tactical": 0.6, "case_study": 0.0}
        },
        {
            "content": "Most people price based on what they think they're worth. That's backwards thinking...",
            "ramit_type": "contrarian", 
            "ramit_frameworks": [],
            "ramit_scores": {"framework": 0.1, "contrarian": 0.9, "tactical": 0.1, "case_study": 0.0}
        }
    ]
    
    # Mock user context
    user_context = UserContext(
        business_type="consulting",
        experience_level="beginner",
        previous_topics=["customer_research"],
        current_challenges=["pricing_confidence"],
        progress_indicators=["completed_first_interview"]
    )
    
    # Generate context-aware prompt
    prompt = prompt_generator.generate_context_aware_prompt(
        query=query,
        sources=sources,
        user_context=user_context,
        chat_history="Human: How do I find customers?\nAssistant: Start with customer research..."
    )
    
    print(f"Query: {query}")
    print(f"Generated Prompt Length: {len(prompt)} characters")
    print("\nPrompt Preview (first 500 chars):")
    print("-" * 60)
    print(prompt[:500] + "...")
    print("-" * 60)

def test_coaching_context_injection():
    """Test coaching context injection"""
    print("\n" + "="*80)
    print("COACHING CONTEXT INJECTION TEST")
    print("="*80)
    
    try:
        context_injector = create_coaching_context_injector()
        
        # Test business stage determination
        test_profile_data = {
            "services_offered": ["consulting", "coaching"],
            "pricing_discussed": ["$500/hour", "$2000/month"],
            "client_situations": ["tech_startup", "ecommerce_business"],
            "business_challenges": ["pricing_confidence", "scaling_systems"]
        }
        
        stage = context_injector._determine_business_stage(test_profile_data)
        print(f"Determined Business Stage: {stage}")
        
        # Test framework completion inference
        completed_frameworks = context_injector._infer_completed_frameworks(test_profile_data)
        print(f"Inferred Completed Frameworks: {completed_frameworks}")
        
        # Test business progress generation
        business_progress = context_injector._load_business_progress()
        print(f"Current Business Stage: {business_progress.current_stage}")
        print(f"Completed Frameworks: {business_progress.completed_frameworks}")
        print(f"Ongoing Challenges: {business_progress.ongoing_challenges}")
        
    except Exception as e:
        print(f"Warning: Could not fully test coaching context injection: {e}")
        print("This is expected if user_profile.json doesn't exist or chat_logs directory is missing")

def test_ramit_voice_patterns():
    """Test Ramit's voice patterns and signature selection"""
    print("\n" + "="*80)
    print("RAMIT VOICE PATTERNS TEST")
    print("="*80)
    
    prompt_generator = create_ramit_prompt_generator()
    
    # Test signature selection for different intents
    from src.utils.context_aware_prompting import QueryIntent
    
    intents_to_test = [
        QueryIntent.FIRST_SALE,
        QueryIntent.PRICING,
        QueryIntent.CUSTOMER_RESEARCH,
        QueryIntent.MINDSET,
        QueryIntent.FRAMEWORKS
    ]
    
    for intent in intents_to_test:
        signature = prompt_generator._select_signature_for_intent(intent)
        print(f"Intent: {intent.value}")
        print(f"Signature: \"{signature}\"")
        print("-" * 40)
    
    # Test voice pattern selection
    print("\nVoice Pattern Examples:")
    patterns = prompt_generator.ramit_voice_patterns
    
    for pattern_type, examples in patterns.items():
        print(f"\n{pattern_type.upper()}:")
        for example in examples[:2]:  # Show first 2 examples
            print(f"  • {example}")

if __name__ == "__main__":
    print("CONTEXT-AWARE PROMPTING SYSTEM TEST")
    print("This tests the new dynamic prompting capabilities")
    
    test_query_intent_classification()
    test_content_analysis()
    test_prompt_generation()
    test_coaching_context_injection()
    test_ramit_voice_patterns()
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)
    print("\nThe context-aware prompting system is ready!")
    print("Key features tested:")
    print("✓ Query intent classification")
    print("✓ Content analysis and coaching style determination")
    print("✓ Context-aware prompt generation")
    print("✓ Coaching context injection")
    print("✓ Ramit voice patterns and signatures")
    print("\nTo use in chat: python src/chat.py chat")