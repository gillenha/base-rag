"""
Configurable Context-Aware Prompting System

This module implements dynamic prompt generation that adapts based on query intent,
retrieved content types, and user context to deliver authentic expert-style coaching.
Configurable for any expert through expert_config.yaml.
"""

import re
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from .expert_analyzer import load_expert_config

class QueryIntent(Enum):
    """Dynamically populated from config"""
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
    expert_framework_score: float
    expert_contrarian_score: float
    expert_tactical_score: float
    expert_case_study_score: float
    expert_mindset_score: float
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

class ConfigurablePromptGenerator:
    """
    Generates context-aware prompts that adapt to query intent and content
    Configurable for any expert through expert_config.yaml
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize prompt generator with expert configuration
        
        Args:
            config_path: Path to expert configuration file
        """
        self.config = load_expert_config(config_path)
        self.expert_profile = self.config.get('expert_profile', {})
        self.expert_name = self.expert_profile.get('name', 'Expert')
        
        # Initialize components from config
        self.query_classifiers = self._initialize_query_classifiers()
        self.voice_patterns = self._initialize_voice_patterns()
        self.coaching_frameworks = self._initialize_coaching_frameworks()
        self.response_templates = self._initialize_response_templates()
        self.signature_phrases = self._initialize_signature_phrases()
        
    def _initialize_query_classifiers(self) -> Dict[str, List[str]]:
        """Initialize patterns for classifying query intent from config"""
        classifiers = {}
        intent_config = self.config.get('query_intent_classification', {})
        
        for intent, intent_data in intent_config.items():
            if isinstance(intent_data, dict):
                keywords = intent_data.get('keywords', [])
                classifiers[intent] = keywords
            elif isinstance(intent_data, list):
                classifiers[intent] = intent_data
        
        # Add general as fallback
        if 'general' not in classifiers:
            classifiers['general'] = []
            
        return classifiers
    
    def _initialize_voice_patterns(self) -> Dict[str, List[str]]:
        """Initialize expert's distinctive voice patterns from config"""
        voice_patterns = self.config.get('voice_patterns', {})
        
        # Ensure all required pattern types exist
        default_patterns = {
            "contrarian_openers": [
                "Here's where most people get this wrong:",
                "Conventional wisdom says X, but that's backwards.",
                "Everyone tells you to do X. That's terrible advice."
            ],
            "framework_introductions": [
                "Here's the exact framework I use:",
                "Let me walk you through the system:",
                "This is how the process works:"
            ],
            "tactical_language": [
                "Here's exactly what to do:",
                "Use this exact approach:",
                "Follow these specific steps:"
            ],
            "mindset_shifts": [
                "The psychology behind this is:",
                "Most people have limiting beliefs about:",
                "The mental model you need is:"
            ],
            "case_study_setups": [
                "Let me tell you about someone who:",
                "Here's a real example:",
                "I worked with someone who:"
            ],
            "expert_signatures": [
                "Focus on the fundamentals.",
                "Test everything.",
                "Start before you're ready."
            ]
        }
        
        # Merge config patterns with defaults
        for pattern_type, default_phrases in default_patterns.items():
            if pattern_type not in voice_patterns:
                voice_patterns[pattern_type] = default_phrases
                
        return voice_patterns
    
    def _initialize_coaching_frameworks(self) -> Dict[str, str]:
        """Initialize expert's core frameworks from config"""
        coaching_frameworks = {}
        frameworks_config = self.config.get('frameworks', {})
        
        for framework_name, framework_data in frameworks_config.items():
            if isinstance(framework_data, dict):
                description = framework_data.get('description', '')
                keywords = framework_data.get('keywords', [])
                
                # Build framework description
                framework_text = f"{framework_name.upper()} FRAMEWORK:\\n"
                if description:
                    framework_text += f"- {description}\\n"
                if keywords:
                    framework_text += f"- Key components: {', '.join(keywords)}\\n"
                    
                coaching_frameworks[framework_name] = framework_text
        
        return coaching_frameworks
    
    def _initialize_response_templates(self) -> Dict[CoachingStyle, str]:
        """Initialize response templates for different coaching styles"""
        expert_name = self.expert_name
        
        return {
            CoachingStyle.FRAMEWORK_FOCUSED: f"""
You're asking about {{topic}}, and {expert_name} has a specific framework for this.

{{expert_framework}}

{{context_content}}

Here's how to apply this framework to your situation:
{{tactical_steps}}

Remember: {{expert_principle}}
""",
            
            CoachingStyle.CONTRARIAN_CHALLENGE: f"""
{{contrarian_opener}}

{{context_content}}

Here's what you should do instead:
{{alternative_approach}}

This works because: {{underlying_principle}}
""",
            
            CoachingStyle.TACTICAL_EXECUTION: f"""
{{tactical_opener}}

{{context_content}}

Step-by-step process:
{{detailed_steps}}

{{expert_signature}}
""",
            
            CoachingStyle.MINDSET_SHIFT: f"""
{{mindset_opener}}

{{context_content}}

The psychology behind this:
{{psychological_insight}}

How to reframe this: {{reframe_approach}}
""",
            
            CoachingStyle.CASE_STUDY_DRIVEN: f"""
{{case_study_opener}}

{{student_example}}

{{context_content}}

The lesson here: {{key_takeaway}}

How this applies to you: {{application}}
""",
            
            CoachingStyle.DIRECT_TEACHING: f"""
{{direct_opener}}

{{context_content}}

Key principles:
{{core_principles}}

{{expert_signature}}
"""
        }
    
    def _initialize_signature_phrases(self) -> Dict[str, str]:
        """Initialize expert's signature phrases for different contexts"""
        signatures = self.config.get('signature_phrases_by_context', {})
        
        # Use general signature as fallback
        general_signature = signatures.get('general', 'Focus on the fundamentals.')
        
        # Ensure all contexts have signatures
        default_contexts = ['first_sale', 'customer_research', 'pricing', 'offers', 
                          'mindset', 'frameworks', 'tactical', 'general']
        
        for context in default_contexts:
            if context not in signatures:
                signatures[context] = general_signature
                
        return signatures
    
    def classify_query_intent(self, query: str) -> str:
        """Classify the intent of a user query"""
        query_lower = query.lower()
        
        # Calculate scores for each intent
        intent_scores = {}
        for intent, keywords in self.query_classifiers.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return intent with highest score, default to "general"
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        else:
            return "general"
    
    def analyze_retrieved_content(self, sources: List[Dict[str, Any]]) -> ContentAnalysis:
        """Analyze retrieved content to understand what type of response to generate"""
        expert_prefix = self.expert_name.lower().replace(' ', '_')
        
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
            # Extract expert-specific metadata (support both old ramit_ prefix and new configurable prefix)
            expert_type = source.get(f"{expert_prefix}_primary_type") or source.get("ramit_primary_type")
            if expert_type:
                primary_content_types.append(expert_type)
            
            # Aggregate scores (support both old and new formats)
            expert_scores = {}
            expert_scores["framework"] = source.get(f"{expert_prefix}_framework_score", 0) or source.get("ramit_framework_score", 0)
            expert_scores["contrarian"] = source.get(f"{expert_prefix}_contrarian_score", 0) or source.get("ramit_contrarian_score", 0)
            expert_scores["tactical"] = source.get(f"{expert_prefix}_tactical_score", 0) or source.get("ramit_tactical_score", 0)
            expert_scores["case_study"] = source.get(f"{expert_prefix}_case_study_score", 0) or source.get("ramit_case_study_score", 0)
            expert_scores["mindset"] = source.get(f"{expert_prefix}_mindset_score", 0) or source.get("ramit_mindset_score", 0)
            
            total_framework_score += expert_scores.get("framework", 0)
            total_contrarian_score += expert_scores.get("contrarian", 0)
            total_tactical_score += expert_scores.get("tactical", 0)
            total_case_study_score += expert_scores.get("case_study", 0)
            total_mindset_score += expert_scores.get("mindset", 0)
            
            # Extract frameworks (support both old and new formats)
            frameworks_str = source.get(f"{expert_prefix}_frameworks", "") or source.get("ramit_frameworks", "")
            if frameworks_str:
                frameworks = [f.strip() for f in frameworks_str.split(",") if f.strip()]
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
            expert_framework_score=total_framework_score / num_sources,
            expert_contrarian_score=total_contrarian_score / num_sources,
            expert_tactical_score=total_tactical_score / num_sources,
            expert_case_study_score=total_case_study_score / num_sources,
            expert_mindset_score=total_mindset_score / num_sources,
            dominant_frameworks=list(set(dominant_frameworks)),
            contrarian_indicators=contrarian_indicators,
            case_study_examples=case_study_examples
        )
    
    def determine_coaching_style(self, query_intent: str, content_analysis: ContentAnalysis) -> CoachingStyle:
        """Determine the appropriate coaching style based on query and content"""
        
        # High contrarian score = challenge conventional thinking
        if content_analysis.expert_contrarian_score > 0.5:
            return CoachingStyle.CONTRARIAN_CHALLENGE
        
        # High framework score = teach systematic approach
        if content_analysis.expert_framework_score > 0.5:
            return CoachingStyle.FRAMEWORK_FOCUSED
        
        # High case study score = use examples
        if content_analysis.expert_case_study_score > 0.5:
            return CoachingStyle.CASE_STUDY_DRIVEN
        
        # High tactical score = provide specific steps
        if content_analysis.expert_tactical_score > 0.5:
            return CoachingStyle.TACTICAL_EXECUTION
        
        # Mindset queries = address psychology
        if query_intent == "mindset":
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
        """Build context string from sources with expert-specific annotations"""
        context_parts = []
        expert_prefix = self.expert_name.lower().replace(' ', '_')
        
        for source in sources:
            content = source.get("content", "")
            expert_type = source.get(f"{expert_prefix}_primary_type") or source.get("ramit_primary_type", "general")
            frameworks_str = source.get(f"{expert_prefix}_frameworks") or source.get("ramit_frameworks", "")
            frameworks = [f.strip() for f in frameworks_str.split(",") if f.strip()] if frameworks_str else []
            
            # Annotate content with metadata
            annotation = f"[Content Type: {expert_type}"
            if frameworks:
                annotation += f", Frameworks: {', '.join(frameworks)}"
            annotation += "]"
            
            context_parts.append(f"{annotation}\\n{content}")
        
        return "\\n\\n".join(context_parts)
    
    def _generate_coaching_components(self, 
                                    query_intent: str,
                                    content_analysis: ContentAnalysis,
                                    coaching_style: CoachingStyle,
                                    user_context: Optional[UserContext]) -> Dict[str, str]:
        """Generate coaching-specific components for the prompt"""
        
        components = {}
        
        # Select appropriate openers based on coaching style
        if coaching_style == CoachingStyle.CONTRARIAN_CHALLENGE:
            components["opener"] = self._select_random(self.voice_patterns.get("contrarian_openers", []))
        elif coaching_style == CoachingStyle.FRAMEWORK_FOCUSED:
            components["opener"] = self._select_random(self.voice_patterns.get("framework_introductions", []))
        elif coaching_style == CoachingStyle.TACTICAL_EXECUTION:
            components["opener"] = self._select_random(self.voice_patterns.get("tactical_language", []))
        elif coaching_style == CoachingStyle.MINDSET_SHIFT:
            components["opener"] = self._select_random(self.voice_patterns.get("mindset_shifts", []))
        elif coaching_style == CoachingStyle.CASE_STUDY_DRIVEN:
            components["opener"] = self._select_random(self.voice_patterns.get("case_study_setups", []))
        
        # Add relevant framework content
        if content_analysis.dominant_frameworks:
            framework_name = content_analysis.dominant_frameworks[0]
            if framework_name in self.coaching_frameworks:
                components["framework_content"] = self.coaching_frameworks[framework_name]
        
        # Add expert signature based on query intent
        components["signature"] = self._select_signature_for_intent(query_intent)
        
        # Add user context if available
        if user_context:
            components["user_context"] = self._format_user_context(user_context)
        
        return components
    
    def _build_dynamic_prompt(self, 
                            query: str,
                            query_intent: str,
                            coaching_style: CoachingStyle,
                            components: Dict[str, str],
                            context_content: str,
                            chat_history: str,
                            user_context: Optional[UserContext]) -> str:
        """Build the final dynamic prompt"""
        
        expert_profile = self.expert_profile
        expert_name = expert_profile.get('name', 'Expert')
        teaching_style = expert_profile.get('teaching_style', 'Direct and systematic')
        expertise_domain = expert_profile.get('expertise_domain', 'their field')
        signature_approach = expert_profile.get('signature_approach', 'frameworks and systematic approaches')
        
        # Base coaching personality
        base_prompt = f"""You are {expert_name} coaching through your course materials. Your response style should match {expert_name}'s distinctive approach:

{expert_name.upper()}'S COACHING CHARACTERISTICS:
- Teaching style: {teaching_style}
- Expertise domain: {expertise_domain}
- Signature approach: {signature_approach}
- Uses specific frameworks and systematic approaches
- Provides actionable advice with clear implementation steps
- References real examples and case studies when available
- Addresses both practical tactics and underlying psychology

QUERY ANALYSIS:
- Intent: {query_intent}
- Coaching Style: {coaching_style.value}
- User Query: "{query}"

RESPONSE STRATEGY:
"""
        
        # Add coaching style specific instructions
        if coaching_style == CoachingStyle.CONTRARIAN_CHALLENGE:
            base_prompt += """
- Start by challenging conventional thinking
- Explain why typical advice fails
- Provide the expert's alternative approach
- Back it up with evidence from the content
"""
        elif coaching_style == CoachingStyle.FRAMEWORK_FOCUSED:
            base_prompt += """
- Structure response around the expert's specific framework
- Break down the systematic approach
- Show how components connect
- Provide implementation guidance
"""
        elif coaching_style == CoachingStyle.TACTICAL_EXECUTION:
            base_prompt += """
- Provide specific, actionable steps
- Include exact scripts and language when available
- Give concrete examples
- Focus on immediate implementation
"""
        elif coaching_style == CoachingStyle.MINDSET_SHIFT:
            base_prompt += """
- Address underlying psychology
- Identify limiting beliefs or mental blocks
- Reframe the mental model
- Connect mindset to practical action
"""
        elif coaching_style == CoachingStyle.CASE_STUDY_DRIVEN:
            base_prompt += """
- Lead with student examples or case studies
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
            base_prompt += f"\\n{expert_name.upper()} SIGNATURE: End with \"{components['signature']}\""
        
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
- Respond as {expert_name} would, using their voice and methodology
- Reference specific content from the retrieved materials
- Adapt your coaching style to the analysis above
- Be direct, practical, and framework-driven when appropriate
- Challenge assumptions when content supports it
- Provide specific next steps
"""
        
        return base_prompt
    
    def _select_random(self, options: List[str]) -> str:
        """Select a random option from a list"""
        return random.choice(options) if options else ""
    
    def _select_signature_for_intent(self, query_intent: str) -> str:
        """Select appropriate expert signature based on query intent"""
        return self.signature_phrases.get(query_intent, self.signature_phrases.get('general', 'Focus on the fundamentals.'))
    
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
def create_expert_prompt_generator(config_path: Optional[str] = None) -> ConfigurablePromptGenerator:
    """Create and return a configured expert prompt generator"""
    return ConfigurablePromptGenerator(config_path)