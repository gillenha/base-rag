"""
Coaching Context Injection System

This module enriches responses with user-specific context, progress tracking,
and framework connections to deliver personalized Ramit-style coaching.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

@dataclass
class CoachingSession:
    """Represents a coaching session context"""
    session_date: str
    topics_discussed: List[str]
    frameworks_introduced: List[str]
    action_items: List[str]
    progress_indicators: List[str]
    challenges_identified: List[str]

@dataclass
class BusinessProgress:
    """Tracks user's business development progress"""
    current_stage: str  # idea, validation, first_sale, scaling, optimizing
    completed_frameworks: List[str]
    revenue_milestones: List[str]
    client_count: int
    pricing_evolution: List[str]
    recent_wins: List[str]
    ongoing_challenges: List[str]

class CoachingContextInjector:
    """
    Injects coaching context to personalize responses based on user history,
    progress, and current business situation.
    """
    
    def __init__(self, user_profile_path: str = "./user_profile.json", 
                 chat_logs_dir: str = "./chat_logs"):
        self.user_profile_path = user_profile_path
        self.chat_logs_dir = Path(chat_logs_dir)
        
        # Framework progression map
        self.framework_progression = self._initialize_framework_progression()
        
        # Business stage definitions
        self.business_stages = self._initialize_business_stages()
        
        # Ramit's progressive coaching approach
        self.coaching_progressions = self._initialize_coaching_progressions()
    
    def _initialize_framework_progression(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the logical progression of Ramit's frameworks"""
        return {
            "beginner_path": {
                "sequence": [
                    "mindset_foundation",
                    "business_idea_validation", 
                    "customer_research",
                    "winning_offer",
                    "first_sale",
                    "profit_playbook"
                ],
                "dependencies": {
                    "customer_research": ["mindset_foundation"],
                    "winning_offer": ["customer_research"],
                    "first_sale": ["winning_offer", "customer_research"],
                    "profit_playbook": ["first_sale"]
                }
            },
            "intermediate_path": {
                "sequence": [
                    "pricing_optimization",
                    "scaling_systems",
                    "advanced_selling",
                    "client_retention",
                    "revenue_optimization"
                ],
                "dependencies": {
                    "pricing_optimization": ["first_sale"],
                    "scaling_systems": ["profit_playbook"],
                    "advanced_selling": ["first_sale"],
                    "revenue_optimization": ["scaling_systems"]
                }
            },
            "advanced_path": {
                "sequence": [
                    "business_automation",
                    "team_building",
                    "multiple_revenue_streams",
                    "market_expansion",
                    "exit_strategies"
                ],
                "dependencies": {
                    "business_automation": ["scaling_systems"],
                    "team_building": ["business_automation"],
                    "multiple_revenue_streams": ["revenue_optimization"]
                }
            }
        }
    
    def _initialize_business_stages(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business stage definitions and characteristics"""
        return {
            "idea": {
                "description": "Exploring business ideas, no customers yet",
                "key_frameworks": ["mindset_foundation", "business_idea_validation"],
                "typical_challenges": ["perfectionism", "analysis paralysis", "fear of failure"],
                "ramit_focus": "Start before you're ready, validate quickly",
                "next_milestone": "First customer interview"
            },
            "validation": {
                "description": "Validating ideas through customer research",
                "key_frameworks": ["customer_research", "winning_offer"],
                "typical_challenges": ["finding customers to interview", "pricing uncertainty"],
                "ramit_focus": "Customer research is everything",
                "next_milestone": "First paying customer"
            },
            "first_sale": {
                "description": "Working toward or just achieved first sale",
                "key_frameworks": ["authentic_selling", "profit_playbook"],
                "typical_challenges": ["scaling to second customer", "pricing confidence"],
                "ramit_focus": "One customer to $1000 business",
                "next_milestone": "Consistent monthly revenue"
            },
            "scaling": {
                "description": "Multiple customers, systemizing processes",
                "key_frameworks": ["scaling_systems", "advanced_selling"],
                "typical_challenges": ["time management", "quality consistency"],
                "ramit_focus": "Systems beat goals",
                "next_milestone": "Predictable revenue"
            },
            "optimizing": {
                "description": "Established business, optimizing for growth",
                "key_frameworks": ["revenue_optimization", "business_automation"],
                "typical_challenges": ["team management", "market expansion"],
                "ramit_focus": "Optimize what works, test new channels",
                "next_milestone": "7-figure business or exit"
            }
        }
    
    def _initialize_coaching_progressions(self) -> Dict[str, List[str]]:
        """Initialize Ramit's progressive coaching questions and follow-ups"""
        return {
            "customer_research": [
                "Have you talked to 10 potential customers yet?",
                "What exact language are customers using to describe their problem?",
                "What's the biggest insight from your customer interviews?",
                "How are you testing demand before building anything?"
            ],
            "pricing": [
                "What's your pricing based on - costs or value?",
                "Have you tested higher prices yet?",
                "What objections are you getting about price?",
                "How are you positioning this as an investment?"
            ],
            "first_sale": [
                "What's your biggest obstacle to getting your first sale?",
                "How many sales conversations have you had?",
                "What's your follow-up process?",
                "Are you asking for the sale directly?"
            ],
            "scaling": [
                "What systems are you putting in place?",
                "How are you tracking your key metrics?",
                "What's working that you can do more of?",
                "Where are the bottlenecks in your process?"
            ]
        }
    
    def analyze_user_context(self) -> Tuple[BusinessProgress, List[CoachingSession]]:
        """Analyze user's current context from profile and chat history"""
        
        # Load user profile
        business_progress = self._load_business_progress()
        
        # Analyze recent coaching sessions
        recent_sessions = self._analyze_recent_sessions()
        
        return business_progress, recent_sessions
    
    def _load_business_progress(self) -> BusinessProgress:
        """Load and analyze business progress from user profile"""
        try:
            with open(self.user_profile_path, 'r') as f:
                profile_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            profile_data = {}
        
        # Extract business indicators
        services = profile_data.get('services_offered', [])
        pricing = profile_data.get('pricing_discussed', [])
        challenges = profile_data.get('business_challenges', [])
        client_situations = profile_data.get('client_situations', [])
        
        # Determine current stage
        current_stage = self._determine_business_stage(profile_data)
        
        # Extract completed frameworks (inferred from conversation topics)
        completed_frameworks = self._infer_completed_frameworks(profile_data)
        
        return BusinessProgress(
            current_stage=current_stage,
            completed_frameworks=completed_frameworks,
            revenue_milestones=self._extract_revenue_milestones(profile_data),
            client_count=len(client_situations),
            pricing_evolution=pricing,
            recent_wins=self._extract_wins(profile_data),
            ongoing_challenges=challenges
        )
    
    def _analyze_recent_sessions(self, days_back: int = 7) -> List[CoachingSession]:
        """Analyze recent coaching sessions from chat logs"""
        sessions = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        if not self.chat_logs_dir.exists():
            return sessions
        
        # Process recent chat logs
        for log_file in self.chat_logs_dir.glob("*.md"):
            try:
                # Extract date from filename (YYYYMMDD_HHMMSS.md)
                date_str = log_file.stem[:8]
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if file_date >= cutoff_date:
                    session = self._parse_coaching_session(log_file)
                    if session:
                        sessions.append(session)
            except (ValueError, IndexError):
                continue
        
        return sorted(sessions, key=lambda x: x.session_date, reverse=True)
    
    def _parse_coaching_session(self, log_file: Path) -> Optional[CoachingSession]:
        """Parse a coaching session from a chat log file"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return None
        
        # Extract topics, frameworks, and action items
        topics = self._extract_topics_from_content(content)
        frameworks = self._extract_frameworks_from_content(content)
        action_items = self._extract_action_items_from_content(content)
        progress_indicators = self._extract_progress_indicators(content)
        challenges = self._extract_challenges_from_content(content)
        
        if topics or frameworks:  # Only create session if substantial content
            return CoachingSession(
                session_date=log_file.stem,
                topics_discussed=topics,
                frameworks_introduced=frameworks,
                action_items=action_items,
                progress_indicators=progress_indicators,
                challenges_identified=challenges
            )
        
        return None
    
    def inject_coaching_context(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Inject coaching context based on user's journey and current situation"""
        
        business_progress, recent_sessions = self.analyze_user_context()
        
        # Generate context-aware coaching elements
        coaching_context = {
            "business_stage_guidance": self._generate_stage_guidance(business_progress),
            "framework_progression": self._suggest_next_frameworks(business_progress),
            "personalized_questions": self._generate_personalized_questions(query, business_progress),
            "progress_acknowledgment": self._acknowledge_progress(business_progress, recent_sessions),
            "ramit_connection": self._connect_to_ramit_methodology(query, business_progress),
            "next_steps_suggestion": self._suggest_next_steps(query, business_progress),
            "challenge_addressing": self._address_ongoing_challenges(business_progress)
        }
        
        return coaching_context
    
    def _determine_business_stage(self, profile_data: Dict[str, Any]) -> str:
        """Determine current business stage from profile data"""
        services = profile_data.get('services_offered', [])
        pricing = profile_data.get('pricing_discussed', [])
        clients = profile_data.get('client_situations', [])
        challenges = profile_data.get('business_challenges', [])
        
        # Stage determination logic
        if not services and not pricing:
            return "idea"
        elif services and not clients:
            return "validation"
        elif len(clients) <= 1:
            return "first_sale"
        elif len(clients) <= 5:
            return "scaling"
        else:
            return "optimizing"
    
    def _infer_completed_frameworks(self, profile_data: Dict[str, Any]) -> List[str]:
        """Infer which frameworks the user has likely completed"""
        completed = []
        
        services = profile_data.get('services_offered', [])
        pricing = profile_data.get('pricing_discussed', [])
        clients = profile_data.get('client_situations', [])
        
        if services:
            completed.append("business_idea_validation")
        
        if pricing:
            completed.append("customer_research")
            completed.append("winning_offer")
        
        if clients:
            completed.append("first_sale")
            completed.append("authentic_selling")
        
        return completed
    
    def _generate_stage_guidance(self, business_progress: BusinessProgress) -> str:
        """Generate stage-appropriate guidance"""
        stage_info = self.business_stages.get(business_progress.current_stage, {})
        
        guidance = f"Based on your current stage ({business_progress.current_stage}), "
        guidance += f"Ramit's focus would be: {stage_info.get('ramit_focus', 'Keep building systems')}"
        
        return guidance
    
    def _suggest_next_frameworks(self, business_progress: BusinessProgress) -> str:
        """Suggest the next logical frameworks based on progress"""
        current_stage = business_progress.current_stage
        completed = business_progress.completed_frameworks
        
        # Determine appropriate path
        if current_stage in ["idea", "validation", "first_sale"]:
            path = self.framework_progression["beginner_path"]
        elif current_stage == "scaling":
            path = self.framework_progression["intermediate_path"]
        else:
            path = self.framework_progression["advanced_path"]
        
        # Find next framework
        for framework in path["sequence"]:
            if framework not in completed:
                dependencies = path.get("dependencies", {}).get(framework, [])
                if all(dep in completed for dep in dependencies):
                    return f"Your next framework to master: {framework.replace('_', ' ').title()}"
        
        return "You're ready for advanced optimization strategies"
    
    def _generate_personalized_questions(self, query: str, business_progress: BusinessProgress) -> List[str]:
        """Generate personalized follow-up questions"""
        
        # Map query to coaching progression
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["customer", "research", "interview"]):
            return self.coaching_progressions.get("customer_research", [])[:2]
        elif any(term in query_lower for term in ["price", "pricing", "charge"]):
            return self.coaching_progressions.get("pricing", [])[:2]
        elif any(term in query_lower for term in ["first sale", "first client"]):
            return self.coaching_progressions.get("first_sale", [])[:2]
        elif any(term in query_lower for term in ["scale", "scaling", "grow"]):
            return self.coaching_progressions.get("scaling", [])[:2]
        
        # Default stage-appropriate questions
        stage_info = self.business_stages.get(business_progress.current_stage, {})
        return [f"What's your biggest challenge with {stage_info.get('next_milestone', 'your next step')}?"]
    
    def _acknowledge_progress(self, business_progress: BusinessProgress, recent_sessions: List[CoachingSession]) -> str:
        """Acknowledge user's progress and wins"""
        if business_progress.recent_wins:
            return f"I see you've made progress with: {', '.join(business_progress.recent_wins[-2:])}"
        
        if recent_sessions and recent_sessions[0].progress_indicators:
            return f"Since our last conversation, you've been working on: {recent_sessions[0].progress_indicators[0]}"
        
        return ""
    
    def _connect_to_ramit_methodology(self, query: str, business_progress: BusinessProgress) -> str:
        """Connect current query to broader Ramit methodology"""
        stage_info = self.business_stages.get(business_progress.current_stage, {})
        key_frameworks = stage_info.get("key_frameworks", [])
        
        if key_frameworks:
            return f"This connects to your current focus on {key_frameworks[0].replace('_', ' ')}"
        
        return "This fits into Ramit's systematic approach to business building"
    
    def _suggest_next_steps(self, query: str, business_progress: BusinessProgress) -> str:
        """Suggest concrete next steps based on current context"""
        stage_info = self.business_stages.get(business_progress.current_stage, {})
        next_milestone = stage_info.get("next_milestone", "continuing your progress")
        
        return f"Your next milestone: {next_milestone}"
    
    def _address_ongoing_challenges(self, business_progress: BusinessProgress) -> str:
        """Address ongoing challenges from user's context"""
        if business_progress.ongoing_challenges:
            recent_challenge = business_progress.ongoing_challenges[-1]
            return f"I know you've been working on: {recent_challenge}"
        
        return ""
    
    # Helper methods for content extraction
    def _extract_topics_from_content(self, content: str) -> List[str]:
        """Extract discussed topics from content"""
        topics = []
        content_lower = content.lower()
        
        topic_indicators = [
            "customer research", "pricing", "first sale", "offers", "marketing",
            "mindset", "scaling", "systems", "automation", "frameworks"
        ]
        
        for topic in topic_indicators:
            if topic in content_lower:
                topics.append(topic)
        
        return topics
    
    def _extract_frameworks_from_content(self, content: str) -> List[str]:
        """Extract frameworks mentioned in content"""
        frameworks = []
        content_lower = content.lower()
        
        framework_names = [
            "customer research", "winning offer", "authentic selling", 
            "profit playbook", "business model", "pricing strategy"
        ]
        
        for framework in framework_names:
            if framework in content_lower:
                frameworks.append(framework)
        
        return frameworks
    
    def _extract_action_items_from_content(self, content: str) -> List[str]:
        """Extract action items from content"""
        action_items = []
        
        # Look for imperative language
        action_patterns = [
            r"you should (.+?)[\.\n]",
            r"try (.+?)[\.\n]", 
            r"do (.+?)[\.\n]",
            r"start (.+?)[\.\n]"
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            action_items.extend(matches[:2])  # Limit to avoid noise
        
        return action_items
    
    def _extract_progress_indicators(self, content: str) -> List[str]:
        """Extract progress indicators from content"""
        progress_indicators = []
        
        # Look for progress language
        progress_patterns = [
            r"you've (.+?) already",
            r"you have (.+?) experience",
            r"since you (.+?),",
            r"your (.+?) shows"
        ]
        
        for pattern in progress_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            progress_indicators.extend(matches[:2])
        
        return progress_indicators
    
    def _extract_challenges_from_content(self, content: str) -> List[str]:
        """Extract challenges mentioned in content"""
        challenges = []
        
        challenge_patterns = [
            r"struggling with (.+?)[\.\n]",
            r"difficulty (.+?)[\.\n]",
            r"challenge (.+?)[\.\n]",
            r"problem (.+?)[\.\n]"
        ]
        
        for pattern in challenge_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            challenges.extend(matches[:2])
        
        return challenges
    
    def _extract_revenue_milestones(self, profile_data: Dict[str, Any]) -> List[str]:
        """Extract revenue milestones from profile"""
        pricing = profile_data.get('pricing_discussed', [])
        revenue_indicators = []
        
        for item in pricing:
            # Look for dollar amounts
            dollar_amounts = re.findall(r'\$[\d,]+', str(item))
            revenue_indicators.extend(dollar_amounts)
        
        return revenue_indicators
    
    def _extract_wins(self, profile_data: Dict[str, Any]) -> List[str]:
        """Extract recent wins from profile"""
        # Look for positive indicators in recent data
        progress_updates = profile_data.get('progress_updates', [])
        client_situations = profile_data.get('client_situations', [])
        
        wins = []
        
        # Recent client acquisitions are wins
        if client_situations:
            wins.append(f"acquired {len(client_situations)} clients")
        
        # Recent progress updates
        wins.extend(progress_updates[-2:] if progress_updates else [])
        
        return wins

# Factory function
def create_coaching_context_injector(user_profile_path: str = "./user_profile.json",
                                   chat_logs_dir: str = "./chat_logs") -> CoachingContextInjector:
    """Create and return a configured coaching context injector"""
    return CoachingContextInjector(user_profile_path, chat_logs_dir)