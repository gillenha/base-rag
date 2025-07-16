import os
import glob
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from .expert_analyzer import load_expert_config

class GreetingGenerator:
    """
    Generates personalized greetings based on recent chat history and user profile.
    Now configurable for any expert through YAML configuration.
    """
    
    def __init__(self, chat_logs_dir: str = "./chat_logs", user_profile=None, expert_config_path: Optional[str] = None):
        """
        Initialize the greeting generator.
        
        Args:
            chat_logs_dir: Directory containing chat log files
            user_profile: UserProfile instance
            expert_config_path: Path to expert configuration file
        """
        self.chat_logs_dir = chat_logs_dir
        self.user_profile = user_profile
        
        # Load expert configuration
        try:
            self.expert_config = load_expert_config(expert_config_path)
            self.expert_profile = self.expert_config.get('expert_profile', {})
        except Exception as e:
            print(f"Warning: Could not load expert config: {e}")
            # Fallback to default Ramit configuration
            self.expert_profile = {
                'name': 'Ramit Sethi',
                'expertise_domain': 'Business and Career Development',
                'signature_approach': 'Systematic frameworks with psychology'
            }
    
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
        Identify common themes from recent conversations using expert-specific keywords.
        
        Args:
            topics: List of recent conversation topics
            
        Returns:
            List of identified themes
        """
        if not topics:
            return []
        
        # Get theme keywords from expert configuration
        theme_keywords = self._get_domain_specific_themes()
        
        theme_counts = {theme: 0 for theme in theme_keywords.keys()}
        
        for topic in topics:
            question_lower = topic["question"].lower()
            for theme, keywords in theme_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    theme_counts[theme] += 1
        
        # Return themes that appeared in at least 2 conversations
        return [theme for theme, count in theme_counts.items() if count >= 2]
    
    def _get_domain_specific_themes(self) -> Dict[str, List[str]]:
        """
        Get domain-specific themes based on expert's expertise domain.
        
        Returns:
            Dictionary mapping theme names to keyword lists
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        
        if 'career' in domain or 'job' in domain:
            # Career coaching themes
            return {
                "job_search": ["job search", "job hunt", "job application", "career change", "new position"],
                "interviews": ["interview", "interviewing", "job interview", "behavioral questions"],
                "salary_negotiation": ["salary", "negotiation", "raise", "compensation", "pay"],
                "networking": ["networking", "professional relationships", "industry connections"],
                "career_strategy": ["career strategy", "career planning", "career advancement"],
                "resume": ["resume", "cv", "application", "portfolio"],
                "skills": ["skills", "training", "certification", "development"],
                "confidence": ["confidence", "impostor syndrome", "self-worth", "mindset"]
            }
        else:
            # Business coaching themes (default)
            return {
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
    
    def _get_expert_title(self) -> str:
        """
        Generate expert-specific title based on domain.
        
        Returns:
            Expert title string
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        expert_name = self.expert_profile.get('name', 'Expert')
        
        if 'career' in domain or 'job' in domain:
            return f"{expert_name} - Career Coach"
        elif 'business' in domain:
            return f"{expert_name} - Business Coach"
        else:
            return f"{expert_name} - Coach"
    
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
            first_time_greetings = self._get_domain_specific_greetings()
            greeting_parts.append(random.choice(first_time_greetings))
        
        # Add context from recent conversations
        if themes:
            theme_descriptions = self._get_theme_descriptions()
            
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
            prompt = self._get_domain_specific_continuation_prompt(themes)
            greeting_parts.append(prompt)
        else:
            # Different prompts for first-time users
            first_time_prompts = self._get_domain_specific_first_time_prompts()
            greeting_parts.append(random.choice(first_time_prompts))
        
        return " ".join(greeting_parts)
    
    def _get_domain_specific_greetings(self) -> List[str]:
        """
        Get domain-specific greeting messages.
        
        Returns:
            List of greeting messages
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        expert_name = self.expert_profile.get('name', 'Expert')
        
        if 'career' in domain or 'job' in domain:
            return [
                f"Welcome! I'm your {expert_name} career coach, ready to help you advance your career and achieve your professional goals.",
                f"Hello! I'm here to guide you through career development using proven strategies and frameworks.",
                f"Welcome to your career coaching session! I'm ready to help you land your dream job and advance your career.",
                f"Hi there! I'm your personal career coach, trained to help you succeed in your professional journey."
            ]
        else:
            # Business coaching (default)
            return [
                f"Welcome! I'm your {expert_name} business coach, ready to help you build and grow your business.",
                f"Hello! I'm here to guide you through building a successful business using proven frameworks.",
                f"Welcome to your business coaching session! I'm ready to help you turn your business ideas into reality.",
                f"Hi there! I'm your personal business coach, trained to help you succeed."
            ]
    
    def _get_theme_descriptions(self) -> Dict[str, str]:
        """
        Get domain-specific theme descriptions.
        
        Returns:
            Dictionary mapping theme names to descriptions
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        
        if 'career' in domain or 'job' in domain:
            return {
                "job_search": "job search strategies",
                "interviews": "interview preparation",
                "salary_negotiation": "salary negotiation",
                "networking": "professional networking",
                "career_strategy": "career advancement",
                "resume": "resume optimization",
                "skills": "skill development",
                "confidence": "career confidence"
            }
        else:
            return {
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
    
    def _get_domain_specific_continuation_prompt(self, themes: List[str]) -> str:
        """
        Get domain-specific continuation prompt based on themes.
        
        Args:
            themes: List of conversation themes
            
        Returns:
            Continuation prompt string
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        
        if 'career' in domain or 'job' in domain:
            if "job_search" in themes:
                return "Would you like to continue working on your job search strategy, or is there something else on your mind?"
            elif "interviews" in themes:
                return "Ready to continue with interview preparation, or do you have a new career challenge to tackle?"
            elif "salary_negotiation" in themes:
                return "Should we dive deeper into salary negotiation tactics, or explore a different aspect of your career?"
            else:
                return "What would you like to work on for your career today?"
        else:
            # Business coaching prompts
            if "pricing" in themes:
                return "Would you like to continue working on your pricing strategy, or is there something else on your mind?"
            elif "clients" in themes:
                return "Ready to continue with client acquisition strategies, or do you have a new challenge to tackle?"
            elif "services" in themes:
                return "Should we dive deeper into your service offerings, or explore a different aspect of your business?"
            else:
                return "What would you like to work on today?"
    
    def _get_domain_specific_first_time_prompts(self) -> List[str]:
        """
        Get domain-specific first-time user prompts.
        
        Returns:
            List of first-time prompts
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        
        if 'career' in domain or 'job' in domain:
            return [
                "What's the most important thing you'd like to focus on for your career right now?",
                "What's the biggest challenge or opportunity you're facing in your career?",
                "What would you like to work on first to advance your career?",
                "What's the most pressing career question on your mind today?"
            ]
        else:
            return [
                "What's the most important thing you'd like to focus on for your business right now?",
                "What's the biggest challenge or opportunity you're facing in your business?",
                "What would you like to work on first to grow your business?",
                "What's the most pressing business question on your mind today?"
            ]
    
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
        self._add_theme_based_suggestions(themes, suggestions)
        
        # Add general suggestions if no specific themes or to fill out the list
        general_suggestions = self._get_domain_specific_general_suggestions()
        
        # Shuffle general suggestions and add them to fill out the list
        random.shuffle(general_suggestions)
        for suggestion in general_suggestions:
            if len(suggestions) < 3 and suggestion not in suggestions:
                suggestions.append(suggestion)
        
        # Add profile-based suggestions
        if profile_info.get("challenges") and len(suggestions) < 3:
            suggestions.append("• Address a specific business challenge you're facing")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _add_theme_based_suggestions(self, themes: List[str], suggestions: List[str]) -> None:
        """
        Add theme-based suggestions to the suggestions list.
        
        Args:
            themes: List of conversation themes
            suggestions: List to add suggestions to (modified in place)
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        
        if 'career' in domain or 'job' in domain:
            if "job_search" in themes:
                suggestions.append("• Continue optimizing your job search strategy")
            if "interviews" in themes:
                suggestions.append("• Practice more interview scenarios")
            if "salary_negotiation" in themes:
                suggestions.append("• Refine your salary negotiation approach")
            if "networking" in themes:
                suggestions.append("• Expand your professional network")
            if "resume" in themes:
                suggestions.append("• Further optimize your resume")
            if "career_strategy" in themes:
                suggestions.append("• Develop your long-term career plan")
        else:
            # Business suggestions
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
    
    def _get_domain_specific_general_suggestions(self) -> List[str]:
        """
        Get domain-specific general suggestions.
        
        Returns:
            List of general suggestions
        """
        domain = self.expert_profile.get('expertise_domain', '').lower()
        
        if 'career' in domain or 'job' in domain:
            return [
                "• Update and optimize your resume for your target roles",
                "• Research companies and roles that align with your career goals",
                "• Practice interviewing and develop compelling career stories",
                "• Build your professional network in your target industry",
                "• Prepare for salary negotiation in your next role",
                "• Develop new skills that advance your career trajectory",
                "• Create a strategic career advancement plan",
                "• Work on building confidence and overcoming career limiting beliefs"
            ]
        else:
            return [
                "• Review your current pricing and see if you can raise rates",
                "• Identify your next ideal client and create a plan to reach them",
                "• Develop a new service package or product",
                "• Work on your business positioning and messaging",
                "• Create a lead generation system for your business",
                "• Analyze your current client base and identify expansion opportunities",
                "• Build a referral system to get more clients",
                "• Develop a passive income stream for your business"
            ]
    
    def get_expert_title(self) -> str:
        """
        Get the expert title for the chat interface.
        
        Returns:
            Expert title string
        """
        return self._get_expert_title() 