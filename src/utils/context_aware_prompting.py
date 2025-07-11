"""
Context-Aware Prompting System for Ramit Sethi Coaching

This module implements dynamic prompt generation that adapts based on query intent,
retrieved content types, and user context to deliver authentic Ramit-style coaching.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QueryIntent(Enum):
    FIRST_SALE = "first_sale"
    CUSTOMER_RESEARCH = "customer_research"
    PRICING = "pricing"
    OFFERS = "offers"
    MINDSET = "mindset"
    FRAMEWORKS = "frameworks"
    CONTRARIAN = "contrarian"
    TACTICAL = "tactical"
    CASE_STUDY = "case_study"
    GENERAL = "general"

class CoachingStyle(Enum):
    FRAMEWORK_FOCUSED = "framework_focused"
    CONTRARIAN_CHALLENGE = "contrarian_challenge"
    TACTICAL_EXECUTION = "tactical_execution"
    MINDSET_SHIFT = "mindset_shift"
    CASE_STUDY_DRIVEN = "case_study_driven"
    DIRECT_TEACHING = "direct_teaching"

@dataclass
class ContentAnalysis:
    """Analysis of retrieved content to inform prompt adaptation"""
    primary_content_types: List[str]
    ramit_framework_score: float
    ramit_contrarian_score: float
    ramit_tactical_score: float
    ramit_case_study_score: float
    ramit_mindset_score: float
    dominant_frameworks: List[str]
    contrarian_indicators: List[str]
    case_study_examples: List[str]

@dataclass
class UserContext:
    """User context for personalized coaching"""
    business_type: Optional[str] = None
    experience_level: str = "beginner"  # beginner, intermediate, advanced
    previous_topics: List[str] = None
    current_challenges: List[str] = None
    progress_indicators: List[str] = None

class RamitPromptGenerator:
    """
    Generates context-aware prompts that adapt to query intent and content
    """
    
    def __init__(self):
        self.query_classifiers = self._initialize_query_classifiers()
        self.ramit_voice_patterns = self._initialize_ramit_voice_patterns()
        self.coaching_frameworks = self._initialize_coaching_frameworks()
        self.response_templates = self._initialize_response_templates()
        
    def _initialize_query_classifiers(self) -> Dict[QueryIntent, List[str]]:
        """Initialize patterns for classifying query intent"""
        return {
            QueryIntent.FIRST_SALE: [
                "first sale", "first client", "get my first", "land my first",
                "initial sale", "first customer", "starting out", "beginning"
            ],
            QueryIntent.CUSTOMER_RESEARCH: [
                "customer research", "mind reading", "understand customers",
                "customer needs", "target audience", "customer interviews"
            ],
            QueryIntent.PRICING: [
                "price", "pricing", "charge", "rates", "how much",
                "cost", "expensive", "cheap", "value"
            ],
            QueryIntent.OFFERS: [
                "offer", "package", "service", "product", "irresistible",
                "compelling", "positioning", "guarantee"
            ],
            QueryIntent.MINDSET: [
                "mindset", "confidence", "fear", "doubt", "believe",
                "psychology", "mental", "invisible scripts", "limiting"
            ],
            QueryIntent.FRAMEWORKS: [
                "framework", "system", "process", "methodology", "approach",
                "strategy", "plan", "structure"
            ],
            QueryIntent.CONTRARIAN: [
                "wrong", "myth", "conventional wisdom", "everyone says",
                "typical advice", "different approach", "contrarian"
            ],
            QueryIntent.TACTICAL: [
                "how to", "steps", "exactly", "specific", "script",
                "template", "checklist", "action", "implement"
            ],
            QueryIntent.CASE_STUDY: [
                "example", "story", "student", "case study", "real",
                "success", "failure", "what happened"
            ]
        }
    
    def _initialize_ramit_voice_patterns(self) -> Dict[str, List[str]]:
        """Initialize Ramit's distinctive voice patterns and phrases"""
        return {
            "contrarian_openers": [
                "Here's where most people get this wrong:",
                "Conventional wisdom says X, but that's completely backwards.",
                "Everyone tells you to do X. That's terrible advice.",
                "The typical approach is to X. That's why most people fail.",
                "You've probably heard that you should X. Ignore that advice."
            ],
            "framework_introductions": [
                "Here's the exact framework I use:",
                "Let me walk you through the system:",
                "This is how the process actually works:",
                "The framework breaks down into these components:",
                "Here's the step-by-step process:"
            ],
            "tactical_language": [
                "Here's exactly what to do:",
                "Use this exact script:",
                "Copy and paste this:",
                "Here's the specific language:",
                "Follow these exact steps:"
            ],
            "mindset_shifts": [
                "The invisible script here is:",
                "Here's the psychology behind this:",
                "Most people have limiting beliefs about:",
                "The mental model you need is:",
                "Change your money dial on:"
            ],
            "case_study_setups": [
                "Let me tell you about one of my students:",
                "Here's a real example from the course:",
                "I worked with someone who had this exact problem:",
                "This student's transformation shows:",
                "Behind the scenes, here's what really happened:"
            ],
            "ramit_signatures": [
                "Business isn't magic. It's math.",
                "Systems beat goals.",
                "Test everything.",
                "Start before you're ready.",
                "You don't need to be an expert.",
                "Focus on your first paying customer.",
                "Master the fundamentals first."
            ]
        }
    
    def _initialize_coaching_frameworks(self) -> Dict[str, str]:
        """Initialize Ramit's core frameworks and their coaching approaches"""
        return {
            "customer_research": """
CUSTOMER RESEARCH FRAMEWORK:
- Start with customer research, not product development
- Ask about their biggest challenges and dream outcomes
- Use exact language from customer interviews
- Test demand before building anything
- Validate with real conversations, not surveys
""",
            "winning_offer": """
WINNING OFFER FRAMEWORK:
- Anatomy: Problem + Solution + Urgency + Guarantee + Bonuses
- Position as an investment, not a cost
- Make it irresistible by removing all risk
- Use specific, concrete benefits
- Include social proof and case studies
""",
            "authentic_selling": """
AUTHENTIC SELLING FRAMEWORK:
- Build rapport first, sell second
- Understand their real needs before presenting
- Use consultative approach, not pushy tactics
- Handle objections by addressing underlying concerns
- Ask for the sale directly and confidently
""",
            "profit_playbook": """
PROFIT PLAYBOOK FRAMEWORK:
- Define your business model clearly
- Identify all revenue streams
- Map out customer acquisition process
- Build systems for predictable growth
- Focus on metrics that matter
"""
        }
    
    def _initialize_response_templates(self) -> Dict[CoachingStyle, str]:
        """Initialize response templates for different coaching styles"""
        return {
            CoachingStyle.FRAMEWORK_FOCUSED: """
You're asking about {topic}, and there's a specific framework for this.

{ramit_framework}

{context_content}

Here's how to apply this framework to your situation:
{tactical_steps}

Remember: {ramit_principle}
""",
            
            CoachingStyle.CONTRARIAN_CHALLENGE: """
{contrarian_opener}

{context_content}

Here's what you should do instead:
{alternative_approach}

This works because: {underlying_principle}
""",
            
            CoachingStyle.TACTICAL_EXECUTION: """
{tactical_opener}

{context_content}

Step-by-step process:
{detailed_steps}

{ramit_signature}
""",
            
            CoachingStyle.MINDSET_SHIFT: """
{mindset_opener}

{context_content}

The psychology behind this:
{psychological_insight}

How to reframe this: {reframe_approach}
""",
            
            CoachingStyle.CASE_STUDY_DRIVEN: """
{case_study_opener}

{student_example}

{context_content}

The lesson here: {key_takeaway}

How this applies to you: {application}
""",
            
            CoachingStyle.DIRECT_TEACHING: """
{direct_opener}

{context_content}

Key principles:
{core_principles}

{ramit_signature}
"""
        }
    
    def classify_query_intent(self, query: str) -> QueryIntent:
        """Classify the intent of a user query"""
        query_lower = query.lower()
        
        # Calculate scores for each intent
        intent_scores = {}
        for intent, keywords in self.query_classifiers.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return intent with highest score, default to GENERAL
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        else:
            return QueryIntent.GENERAL
    
    def analyze_retrieved_content(self, sources: List[Dict[str, Any]]) -> ContentAnalysis:
        """Analyze retrieved content to understand what type of response to generate"""
        
        # Aggregate content analysis
        total_framework_score = 0.0
        total_contrarian_score = 0.0
        total_tactical_score = 0.0
        total_case_study_score = 0.0
        total_mindset_score = 0.0
        
        primary_content_types = []
        dominant_frameworks = []
        contrarian_indicators = []
        case_study_examples = []
        
        for source in sources:
            # Extract Ramit-specific metadata
            ramit_type = source.get("ramit_type")
            if ramit_type:
                primary_content_types.append(ramit_type)
            
            # Aggregate scores
            scores = source.get("ramit_scores", {})
            total_framework_score += scores.get("framework", 0)
            total_contrarian_score += scores.get("contrarian", 0)
            total_tactical_score += scores.get("tactical", 0)
            total_case_study_score += scores.get("case_study", 0)
            
            # Extract frameworks
            frameworks = source.get("ramit_frameworks", [])
            if frameworks:
                dominant_frameworks.extend(frameworks)
            
            # Look for contrarian content
            content = source.get("content", "").lower()
            if any(phrase in content for phrase in ["wrong", "myth", "conventional wisdom"]):
                contrarian_indicators.append(content[:100])
            
            # Look for case studies
            if any(phrase in content for phrase in ["student", "example", "story"]):
                case_study_examples.append(content[:100])
        
        # Calculate averages
        num_sources = len(sources) if sources else 1
        
        return ContentAnalysis(
            primary_content_types=list(set(primary_content_types)),
            ramit_framework_score=total_framework_score / num_sources,
            ramit_contrarian_score=total_contrarian_score / num_sources,
            ramit_tactical_score=total_tactical_score / num_sources,
            ramit_case_study_score=total_case_study_score / num_sources,
            ramit_mindset_score=total_mindset_score / num_sources,
            dominant_frameworks=list(set(dominant_frameworks)),
            contrarian_indicators=contrarian_indicators,
            case_study_examples=case_study_examples
        )
    
    def determine_coaching_style(self, query_intent: QueryIntent, content_analysis: ContentAnalysis) -> CoachingStyle:
        """Determine the appropriate coaching style based on query and content"""
        
        # High contrarian score = challenge conventional thinking
        if content_analysis.ramit_contrarian_score > 0.5:
            return CoachingStyle.CONTRARIAN_CHALLENGE
        
        # High framework score = teach systematic approach
        if content_analysis.ramit_framework_score > 0.5:
            return CoachingStyle.FRAMEWORK_FOCUSED
        
        # High case study score = use examples
        if content_analysis.ramit_case_study_score > 0.5:
            return CoachingStyle.CASE_STUDY_DRIVEN
        
        # High tactical score = provide specific steps
        if content_analysis.ramit_tactical_score > 0.5:
            return CoachingStyle.TACTICAL_EXECUTION
        
        # Mindset queries = address psychology
        if query_intent == QueryIntent.MINDSET:
            return CoachingStyle.MINDSET_SHIFT
        
        # Default to direct teaching
        return CoachingStyle.DIRECT_TEACHING
    
    def generate_context_aware_prompt(self, 
                                    query: str,
                                    sources: List[Dict[str, Any]], 
                                    user_context: Optional[UserContext] = None,
                                    chat_history: str = "") -> str:
        """Generate a context-aware prompt based on query, sources, and user context"""
        
        # Analyze the query and content
        query_intent = self.classify_query_intent(query)
        content_analysis = self.analyze_retrieved_content(sources)
        coaching_style = self.determine_coaching_style(query_intent, content_analysis)
        
        # Build context string
        context_content = self._build_context_string(sources)
        
        # Generate coaching-specific components
        coaching_components = self._generate_coaching_components(
            query_intent, content_analysis, coaching_style, user_context
        )
        
        # Build the dynamic prompt
        prompt = self._build_dynamic_prompt(
            query, query_intent, coaching_style, coaching_components, 
            context_content, chat_history, user_context
        )
        
        return prompt
    
    def _build_context_string(self, sources: List[Dict[str, Any]]) -> str:
        """Build context string from sources with Ramit-specific annotations"""
        context_parts = []
        
        for source in sources:
            content = source.get("content", "")
            ramit_type = source.get("ramit_type", "general")
            frameworks = source.get("ramit_frameworks", [])
            
            # Annotate content with metadata
            annotation = f"[Content Type: {ramit_type}"
            if frameworks:
                annotation += f", Frameworks: {', '.join(frameworks)}"
            annotation += "]"
            
            context_parts.append(f"{annotation}\\n{content}")
        
        return "\\n\\n".join(context_parts)
    
    def _generate_coaching_components(self, 
                                    query_intent: QueryIntent,
                                    content_analysis: ContentAnalysis,
                                    coaching_style: CoachingStyle,
                                    user_context: Optional[UserContext]) -> Dict[str, str]:
        """Generate coaching-specific components for the prompt"""
        
        components = {}
        
        # Select appropriate openers based on coaching style
        if coaching_style == CoachingStyle.CONTRARIAN_CHALLENGE:
            components["opener"] = self._select_random(self.ramit_voice_patterns["contrarian_openers"])
        elif coaching_style == CoachingStyle.FRAMEWORK_FOCUSED:
            components["opener"] = self._select_random(self.ramit_voice_patterns["framework_introductions"])
        elif coaching_style == CoachingStyle.TACTICAL_EXECUTION:
            components["opener"] = self._select_random(self.ramit_voice_patterns["tactical_language"])
        elif coaching_style == CoachingStyle.MINDSET_SHIFT:
            components["opener"] = self._select_random(self.ramit_voice_patterns["mindset_shifts"])
        elif coaching_style == CoachingStyle.CASE_STUDY_DRIVEN:
            components["opener"] = self._select_random(self.ramit_voice_patterns["case_study_setups"])
        
        # Add relevant framework content
        if content_analysis.dominant_frameworks:
            framework_name = content_analysis.dominant_frameworks[0]
            if framework_name in self.coaching_frameworks:
                components["framework_content"] = self.coaching_frameworks[framework_name]
        
        # Add Ramit signature based on query intent
        components["signature"] = self._select_signature_for_intent(query_intent)
        
        # Add user context if available
        if user_context:
            components["user_context"] = self._format_user_context(user_context)
        
        return components
    
    def _build_dynamic_prompt(self, 
                            query: str,
                            query_intent: QueryIntent,
                            coaching_style: CoachingStyle,
                            components: Dict[str, str],
                            context_content: str,
                            chat_history: str,
                            user_context: Optional[UserContext]) -> str:
        """Build the final dynamic prompt"""
        
        # Base coaching personality
        base_prompt = f"""You are Ramit Sethi coaching through the Earnable course materials. Your response style should match Ramit's distinctive approach:

RAMIT'S COACHING CHARACTERISTICS:
- Direct, no-nonsense communication style
- Uses specific frameworks and systematic approaches
- Challenges conventional wisdom when appropriate
- Provides tactical, actionable advice with exact scripts
- References real student examples and case studies
- Addresses psychology and invisible scripts
- Focuses on testing and validation
- Uses signature phrases: "Business isn't magic, it's math", "Systems beat goals", "Start before you're ready"

QUERY ANALYSIS:
- Intent: {query_intent.value}
- Coaching Style: {coaching_style.value}
- User Query: "{query}"

RESPONSE STRATEGY:
"""
        
        # Add coaching style specific instructions
        if coaching_style == CoachingStyle.CONTRARIAN_CHALLENGE:
            base_prompt += """
- Start by challenging conventional thinking
- Explain why typical advice fails
- Provide Ramit's alternative approach
- Back it up with evidence from the content
"""
        elif coaching_style == CoachingStyle.FRAMEWORK_FOCUSED:
            base_prompt += """
- Structure response around Ramit's specific framework
- Break down the systematic approach
- Show how components connect
- Provide implementation guidance
"""
        elif coaching_style == CoachingStyle.TACTICAL_EXECUTION:
            base_prompt += """
- Provide specific, actionable steps
- Include exact scripts and language
- Give concrete examples
- Focus on immediate implementation
"""
        elif coaching_style == CoachingStyle.MINDSET_SHIFT:
            base_prompt += """
- Address underlying psychology
- Identify invisible scripts or limiting beliefs
- Reframe the mental model
- Connect mindset to practical action
"""
        elif coaching_style == CoachingStyle.CASE_STUDY_DRIVEN:
            base_prompt += """
- Lead with student examples
- Show real transformations
- Extract key lessons
- Apply insights to user's situation
"""
        
        # Add coaching components
        if "opener" in components:
            base_prompt += f"\\nOPENING STYLE: {components['opener']}"
        
        if "framework_content" in components:
            base_prompt += f"\\nRELEVANT FRAMEWORK:\\n{components['framework_content']}"
        
        if "signature" in components:
            base_prompt += f"\\nRAMIT SIGNATURE: End with \"{components['signature']}\""
        
        # Add user context if available
        if user_context:
            base_prompt += f"\\nUSER CONTEXT: {components.get('user_context', '')}"
        
        # Add content and history
        base_prompt += f"""

RETRIEVED CONTENT:
{context_content}

CHAT HISTORY:
{chat_history}

COACHING INSTRUCTIONS:
- Respond as Ramit would, using his voice and methodology
- Reference specific content from the retrieved materials
- Adapt your coaching style to the analysis above
- Be direct, practical, and framework-driven
- Challenge assumptions when content supports it
- Provide specific next steps
"""
        
        return base_prompt
    
    def _select_random(self, options: List[str]) -> str:
        """Select a random option from a list"""
        import random
        return random.choice(options) if options else ""
    
    def _select_signature_for_intent(self, query_intent: QueryIntent) -> str:
        """Select appropriate Ramit signature based on query intent"""
        intent_signatures = {
            QueryIntent.FIRST_SALE: "Focus on your first paying customer.",
            QueryIntent.CUSTOMER_RESEARCH: "Systems beat goals.",
            QueryIntent.PRICING: "Business isn't magic. It's math.",
            QueryIntent.OFFERS: "Test everything.",
            QueryIntent.MINDSET: "Start before you're ready.",
            QueryIntent.FRAMEWORKS: "Master the fundamentals first.",
            QueryIntent.TACTICAL: "You don't need to be an expert."
        }
        
        return intent_signatures.get(query_intent, "Business isn't magic. It's math.")
    
    def _format_user_context(self, user_context: UserContext) -> str:
        """Format user context for inclusion in prompt"""
        context_parts = []
        
        if user_context.business_type:
            context_parts.append(f"Business type: {user_context.business_type}")
        
        if user_context.experience_level:
            context_parts.append(f"Experience level: {user_context.experience_level}")
        
        if user_context.previous_topics:
            context_parts.append(f"Previous topics discussed: {', '.join(user_context.previous_topics)}")
        
        if user_context.current_challenges:
            context_parts.append(f"Current challenges: {', '.join(user_context.current_challenges)}")
        
        return "; ".join(context_parts)

# Factory function for creating prompt generator
def create_ramit_prompt_generator() -> RamitPromptGenerator:
    """Create and return a configured Ramit prompt generator"""
    return RamitPromptGenerator()