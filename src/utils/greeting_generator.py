import os
import glob
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re

class GreetingGenerator:
    """
    Generates personalized greetings based on recent chat history and user profile.
    """
    
    def __init__(self, chat_logs_dir: str = "./chat_logs", user_profile=None):
        """
        Initialize the greeting generator.
        
        Args:
            chat_logs_dir: Directory containing chat log files
            user_profile: UserProfile instance
        """
        self.chat_logs_dir = chat_logs_dir
        self.user_profile = user_profile
    
    def get_recent_chat_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Analyze recent chat logs to understand conversation patterns and topics.
        
        Args:
            days_back: Number of days to look back for recent conversations
            
        Returns:
            Dictionary with analysis of recent conversations
        """
        if not os.path.exists(self.chat_logs_dir):
            return {"topics": [], "last_conversation": None, "conversation_count": 0}
        
        # Get recent chat log files
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_files = []
        
        for file_path in glob.glob(os.path.join(self.chat_logs_dir, "*.md")):
            try:
                # Extract date from filename (format: YYYYMMDD_HHMMSS.md)
                filename = os.path.basename(file_path)
                # Remove the .md extension using os.path.splitext
                filename_without_ext = os.path.splitext(filename)[0]
                date_str = filename_without_ext.split('_')[0] + '_' + filename_without_ext.split('_')[1]
                file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                
                if file_date >= cutoff_date:
                    recent_files.append((file_path, file_date))
            except (ValueError, IndexError):
                continue
        
        # Sort by date (newest first)
        recent_files.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze recent conversations
        topics = []
        last_conversation = None
        
        for file_path, file_date in recent_files[:5]:  # Look at last 5 conversations
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract user questions
                user_sections = re.findall(r'### You\n\n(.*?)\n\n### Coach', content, re.DOTALL)
                
                for question in user_sections:
                    question = question.strip()
                    if question and len(question) > 10:  # Filter out very short questions
                        topics.append({
                            "question": question,
                            "date": file_date,
                            "file": os.path.basename(file_path)
                        })
                
                if not last_conversation and user_sections:
                    last_conversation = {
                        "date": file_date,
                        "question": user_sections[0].strip()[:100] + "..." if len(user_sections[0]) > 100 else user_sections[0].strip()
                    }
                    
            except Exception as e:
                continue
        
        return {
            "topics": topics,
            "last_conversation": last_conversation,
            "conversation_count": len(recent_files)
        }
    
    def identify_conversation_themes(self, topics: List[Dict[str, Any]]) -> List[str]:
        """
        Identify common themes from recent conversations.
        
        Args:
            topics: List of recent conversation topics
            
        Returns:
            List of identified themes
        """
        if not topics:
            return []
        
        # Keywords to identify themes
        theme_keywords = {
            "pricing": ["price", "rate", "charge", "cost", "pricing", "fee", "budget"],
            "clients": ["client", "customer", "prospect", "lead", "referral"],
            "services": ["service", "offer", "package", "deliverable", "solution"],
            "marketing": ["marketing", "advertising", "promotion", "outreach", "social media"],
            "business_growth": ["grow", "scale", "expand", "increase", "growth"],
            "challenges": ["problem", "challenge", "issue", "struggle", "difficulty"],
            "strategy": ["strategy", "plan", "approach", "method", "framework"],
            "website": ["website", "web", "site", "online", "digital"],
            "sales": ["sale", "selling", "close", "proposal", "pitch"]
        }
        
        theme_counts = {theme: 0 for theme in theme_keywords.keys()}
        
        for topic in topics:
            question_lower = topic["question"].lower()
            for theme, keywords in theme_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    theme_counts[theme] += 1
        
        # Return themes that appeared in at least 2 conversations
        return [theme for theme, count in theme_counts.items() if count >= 2]
    
    def generate_greeting(self) -> str:
        """
        Generate a personalized greeting based on recent activity and user profile.
        
        Returns:
            A personalized greeting message
        """
        # Get recent chat analysis
        recent_analysis = self.get_recent_chat_summary()
        themes = self.identify_conversation_themes(recent_analysis["topics"])
        
        # Get user profile info
        profile_info = {}
        if self.user_profile:
            profile_info = self.user_profile.profile.get("business_info", {})
        
        # Generate greeting based on context
        greeting_parts = []
        
        # Welcome back message
        if recent_analysis["conversation_count"] > 0:
            days_since_last = None
            if recent_analysis["last_conversation"]:
                days_since_last = (datetime.now() - recent_analysis["last_conversation"]["date"]).days
            
            if days_since_last and days_since_last > 14:
                greeting_parts.append(f"Welcome back! It's been {days_since_last} days since we last talked.")
            elif days_since_last and days_since_last > 7:
                greeting_parts.append(f"Good to see you again! It's been {days_since_last} days.")
            elif days_since_last and days_since_last > 1:
                greeting_parts.append(f"Welcome back! It's been {days_since_last} days since our last conversation.")
            else:
                greeting_parts.append("Welcome back! I'm here to help you continue building your business.")
        else:
            # First-time user or no recent logs
            first_time_greetings = [
                "Welcome! I'm your Earnable business coach, ready to help you build and grow your business.",
                "Hello! I'm here to guide you through building a successful business using Earnable principles.",
                "Welcome to your business coaching session! I'm ready to help you turn your business ideas into reality.",
                "Hi there! I'm your personal business coach, trained on the Earnable course to help you succeed."
            ]
            greeting_parts.append(random.choice(first_time_greetings))
        
        # Add context from recent conversations
        if themes:
            theme_descriptions = {
                "pricing": "pricing strategies",
                "clients": "client acquisition",
                "services": "service offerings",
                "marketing": "marketing approaches",
                "business_growth": "business growth",
                "challenges": "business challenges",
                "strategy": "business strategy",
                "website": "website development",
                "sales": "sales processes"
            }
            
            theme_list = [theme_descriptions.get(theme, theme) for theme in themes[:3]]
            if len(theme_list) == 1:
                greeting_parts.append(f"I see we've been focusing on {theme_list[0]} recently.")
            elif len(theme_list) == 2:
                greeting_parts.append(f"I see we've been working on {theme_list[0]} and {theme_list[1]}.")
            else:
                greeting_parts.append(f"I see we've been covering {', '.join(theme_list[:-1])}, and {theme_list[-1]}.")
        
        # Add business-specific context
        if profile_info.get("services"):
            services = profile_info["services"]
            if len(services) == 1:
                greeting_parts.append(f"I remember you offer {services[0]}.")
            else:
                service_list = ", ".join(services[:-1]) + f" and {services[-1]}"
                greeting_parts.append(f"I remember you offer {service_list}.")
        
        if profile_info.get("pricing"):
            recent_pricing = profile_info["pricing"].get("recent_sale")
            if recent_pricing:
                greeting_parts.append(f"Your recent work has been in the {recent_pricing} range.")
        
        # Add a helpful prompt
        if recent_analysis["last_conversation"]:
            if "pricing" in themes:
                greeting_parts.append("Would you like to continue working on your pricing strategy, or is there something else on your mind?")
            elif "clients" in themes:
                greeting_parts.append("Ready to continue with client acquisition strategies, or do you have a new challenge to tackle?")
            elif "services" in themes:
                greeting_parts.append("Should we dive deeper into your service offerings, or explore a different aspect of your business?")
            else:
                greeting_parts.append("What would you like to work on today?")
        else:
            # Different prompts for first-time users
            first_time_prompts = [
                "What's the most important thing you'd like to focus on for your business right now?",
                "What's the biggest challenge or opportunity you're facing in your business?",
                "What would you like to work on first to grow your business?",
                "What's the most pressing business question on your mind today?"
            ]
            greeting_parts.append(random.choice(first_time_prompts))
        
        return " ".join(greeting_parts)
    
    def get_quick_start_suggestions(self) -> List[str]:
        """
        Get quick start suggestions based on recent activity and user profile.
        
        Returns:
            List of suggested conversation starters
        """
        recent_analysis = self.get_recent_chat_summary()
        themes = self.identify_conversation_themes(recent_analysis["topics"])
        profile_info = self.user_profile.profile.get("business_info", {}) if self.user_profile else {}
        
        suggestions = []
        
        # Add suggestions based on themes
        if "pricing" in themes:
            suggestions.append("• Continue refining your pricing strategy")
        if "clients" in themes:
            suggestions.append("• Work on client acquisition methods")
        if "services" in themes:
            suggestions.append("• Develop new service packages")
        if "marketing" in themes:
            suggestions.append("• Improve your marketing approach")
        if "website" in themes:
            suggestions.append("• Optimize your website for conversions")
        if "sales" in themes:
            suggestions.append("• Enhance your sales process")
        
        # Add general suggestions if no specific themes or to fill out the list
        general_suggestions = [
            "• Review your current pricing and see if you can raise rates",
            "• Identify your next ideal client and create a plan to reach them",
            "• Develop a new service package or product",
            "• Work on your business positioning and messaging",
            "• Create a lead generation system for your business",
            "• Analyze your current client base and identify expansion opportunities",
            "• Build a referral system to get more clients",
            "• Develop a passive income stream for your business"
        ]
        
        # Shuffle general suggestions and add them to fill out the list
        random.shuffle(general_suggestions)
        for suggestion in general_suggestions:
            if len(suggestions) < 3 and suggestion not in suggestions:
                suggestions.append(suggestion)
        
        # Add profile-based suggestions
        if profile_info.get("challenges") and len(suggestions) < 3:
            suggestions.append("• Address a specific business challenge you're facing")
        
        return suggestions[:3]  # Return top 3 suggestions 