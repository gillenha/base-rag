#!/usr/bin/env python3
"""
Test script to demonstrate the personalized greeting functionality.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.greeting_generator import GreetingGenerator
from src.utils.user_profile import UserProfile

def test_greeting_generator():
    """Test the greeting generator with different scenarios."""
    
    print("Testing Personalized Greeting Generator\n")
    print("=" * 50)
    
    # Initialize user profile and greeting generator
    user_profile = UserProfile(profile_path="./user_profile.json")
    greeting_generator = GreetingGenerator(chat_logs_dir="./chat_logs", user_profile=user_profile)
    
    # Test 1: Generate current greeting
    print("1. Current Greeting:")
    print("-" * 30)
    greeting = greeting_generator.generate_greeting()
    print(greeting)
    print()
    
    # Test 2: Get quick start suggestions
    print("2. Quick Start Suggestions:")
    print("-" * 30)
    suggestions = greeting_generator.get_quick_start_suggestions()
    for suggestion in suggestions:
        print(suggestion)
    print()
    
    # Test 3: Analyze recent chat summary
    print("3. Recent Chat Analysis:")
    print("-" * 30)
    recent_analysis = greeting_generator.get_recent_chat_summary()
    print(f"Total conversations in last 7 days: {recent_analysis['conversation_count']}")
    
    if recent_analysis['last_conversation']:
        print(f"Last conversation: {recent_analysis['last_conversation']['date'].strftime('%Y-%m-%d %H:%M')}")
        print(f"Last question: {recent_analysis['last_conversation']['question'][:100]}...")
    else:
        print("No recent conversations found.")
    
    print(f"Recent topics: {len(recent_analysis['topics'])}")
    print()
    
    # Test 4: Identify themes
    print("4. Identified Themes:")
    print("-" * 30)
    themes = greeting_generator.identify_conversation_themes(recent_analysis['topics'])
    if themes:
        for theme in themes:
            print(f"• {theme}")
    else:
        print("No recurring themes identified.")
    print()
    
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_greeting_generator() 