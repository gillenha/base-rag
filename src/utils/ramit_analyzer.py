"""
Ramit Sethi Content Analyzer

This module analyzes document chunks to identify Ramit-specific characteristics,
frameworks, and terminology, enriching metadata for better semantic retrieval.
"""

import re
from typing import Dict, List, Set, Any
from dataclasses import dataclass
from enum import Enum

class ContentType(Enum):
    FRAMEWORK = "framework"
    MINDSET = "mindset"
    TACTICAL = "tactical"
    CONTRARIAN = "contrarian"
    CASE_STUDY = "case_study"
    TESTING = "testing"
    STORY = "story"
    NUMBERS = "numbers"

@dataclass
class RamitSignature:
    """Represents a signature phrase or concept from Ramit's methodology"""
    phrase: str
    content_type: ContentType
    weight: float  # How strongly this indicates the content type (0.1-1.0)
    context: str = ""  # Additional context about when this applies

class RamitContentAnalyzer:
    """Analyzes content for Ramit Sethi-specific characteristics and frameworks"""
    
    def __init__(self):
        self.signatures = self._initialize_signatures()
        self.frameworks = self._initialize_frameworks()
        self.contrarian_indicators = self._initialize_contrarian_indicators()
        
    def _initialize_signatures(self) -> List[RamitSignature]:
        """Initialize signature phrases and concepts from Ramit's methodology"""
        return [
            # Frameworks and Systems
            RamitSignature("invisible scripts", ContentType.MINDSET, 0.9),
            RamitSignature("money dials", ContentType.FRAMEWORK, 0.8),
            RamitSignature("profit playbook", ContentType.FRAMEWORK, 0.9),
            RamitSignature("customer research", ContentType.TACTICAL, 0.7),
            RamitSignature("winning offer", ContentType.FRAMEWORK, 0.8),
            RamitSignature("authentic selling", ContentType.FRAMEWORK, 0.8),
            RamitSignature("business isn't magic. it's math", ContentType.NUMBERS, 0.9),
            RamitSignature("predictable numbers", ContentType.NUMBERS, 0.7),
            RamitSignature("rich life", ContentType.MINDSET, 0.8),
            
            # Mindset and Psychology
            RamitSignature("i will teach you to be rich", ContentType.MINDSET, 0.9),
            RamitSignature("you don't need to be an expert", ContentType.CONTRARIAN, 0.8),
            RamitSignature("start before you're ready", ContentType.CONTRARIAN, 0.8),
            RamitSignature("stop asking for permission", ContentType.MINDSET, 0.7),
            RamitSignature("most people are wrong about", ContentType.CONTRARIAN, 0.8),
            RamitSignature("conventional wisdom says", ContentType.CONTRARIAN, 0.7),
            
            # Tactical Content
            RamitSignature("test it", ContentType.TESTING, 0.8),
            RamitSignature("validate", ContentType.TESTING, 0.6),
            RamitSignature("step by step", ContentType.TACTICAL, 0.6),
            RamitSignature("exact script", ContentType.TACTICAL, 0.8),
            RamitSignature("word for word", ContentType.TACTICAL, 0.8),
            RamitSignature("copy and paste", ContentType.TACTICAL, 0.7),
            
            # Case Studies and Stories
            RamitSignature("let me tell you about", ContentType.CASE_STUDY, 0.7),
            RamitSignature("student story", ContentType.CASE_STUDY, 0.9),
            RamitSignature("behind the scenes", ContentType.CASE_STUDY, 0.8),
            RamitSignature("teardown", ContentType.CASE_STUDY, 0.9),
            RamitSignature("makeover", ContentType.CASE_STUDY, 0.9),
            
            # Numbers and Metrics
            RamitSignature("dollar", ContentType.NUMBERS, 0.6),  # Dollar amounts
            RamitSignature("conversion", ContentType.NUMBERS, 0.8),
            RamitSignature("figure", ContentType.NUMBERS, 0.7),
            RamitSignature("email list", ContentType.TACTICAL, 0.6),
            RamitSignature("subscribers", ContentType.NUMBERS, 0.5),
        ]
    
    def _initialize_frameworks(self) -> Dict[str, List[str]]:
        """Initialize Ramit's specific frameworks and their key components"""
        return {
            "customer_research": [
                "customer research call", "mind reading", "what keeps you up at night",
                "biggest challenge", "dream outcome", "customer interviews"
            ],
            "winning_offer": [
                "irresistible offer", "anatomy of", "positioning", "guarantee",
                "bonuses", "scarcity", "urgency", "value proposition"
            ],
            "authentic_selling": [
                "sales call", "objection handling", "closing", "follow up",
                "building rapport", "understanding needs", "presentation"
            ],
            "profit_playbook": [
                "business model", "revenue streams", "pricing strategy",
                "client acquisition", "systems", "automation"
            ],
            "testing_framework": [
                "a/b test", "validate", "iterate", "feedback", "metrics",
                "conversion rate", "optimize", "experiment"
            ]
        }
    
    def _initialize_contrarian_indicators(self) -> List[str]:
        """Initialize phrases that indicate contrarian takes"""
        return [
            "most people think", "conventional wisdom", "everyone says",
            "typical advice", "wrong approach", "don't listen to",
            "opposite of what", "counterintuitive", "surprising truth",
            "myth", "misconception", "big mistake", "dead wrong"
        ]
    
    def analyze_content(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content and return enriched metadata with Ramit-specific tags
        
        Args:
            content: The text content to analyze
            metadata: Existing metadata from the document
            
        Returns:
            Enhanced metadata with Ramit-specific semantic tags
        """
        content_lower = content.lower()
        
        # Initialize analysis results
        analysis = {
            "ramit_content_types": set(),
            "ramit_frameworks": set(),
            "ramit_signatures": [],
            "contrarian_score": 0.0,
            "tactical_score": 0.0,
            "framework_score": 0.0,
            "case_study_score": 0.0,
            "mindset_score": 0.0,
            "testing_score": 0.0,
            "numbers_score": 0.0,
            "story_score": 0.0
        }
        
        # Analyze signatures
        self._analyze_signatures(content_lower, analysis)
        
        # Analyze frameworks
        self._analyze_frameworks(content_lower, analysis)
        
        # Analyze contrarian indicators
        self._analyze_contrarian_content(content_lower, analysis)
        
        # Analyze content structure
        self._analyze_content_structure(content, analysis)
        
        # Calculate overall content classification
        primary_type = self._determine_primary_content_type(analysis)
        
        # Enhance metadata (convert lists to strings for ChromaDB compatibility)
        enhanced_metadata = metadata.copy()
        enhanced_metadata.update({
            "ramit_primary_type": primary_type,
            "ramit_content_types": ",".join(analysis["ramit_content_types"]),
            "ramit_frameworks": ",".join(analysis["ramit_frameworks"]),
            "ramit_signatures": ",".join(analysis["ramit_signatures"]),
            "ramit_contrarian_score": analysis["contrarian_score"],
            "ramit_tactical_score": analysis["tactical_score"],
            "ramit_framework_score": analysis["framework_score"],
            "ramit_case_study_score": analysis["case_study_score"],
            "ramit_mindset_score": analysis["mindset_score"],
            "ramit_testing_score": analysis["testing_score"],
            "ramit_numbers_score": analysis["numbers_score"],
            "ramit_story_score": analysis["story_score"],
        })
        
        return enhanced_metadata
    
    def _analyze_signatures(self, content: str, analysis: Dict[str, Any]):
        """Analyze content for Ramit's signature phrases and concepts"""
        for signature in self.signatures:
            if re.search(signature.phrase.lower(), content, re.IGNORECASE):
                analysis["ramit_signatures"].append(signature.phrase)
                analysis["ramit_content_types"].add(signature.content_type.value)
                
                # Add to specific score
                score_key = f"{signature.content_type.value}_score"
                if score_key in analysis:
                    analysis[score_key] += signature.weight
    
    def _analyze_frameworks(self, content: str, analysis: Dict[str, Any]):
        """Analyze content for specific Ramit frameworks"""
        for framework_name, keywords in self.frameworks.items():
            matches = sum(1 for keyword in keywords if keyword in content)
            if matches >= 2:  # Must have at least 2 framework keywords
                analysis["ramit_frameworks"].add(framework_name)
                analysis["framework_score"] += matches * 0.2
    
    def _analyze_contrarian_content(self, content: str, analysis: Dict[str, Any]):
        """Analyze content for contrarian takes and perspectives"""
        contrarian_matches = sum(1 for indicator in self.contrarian_indicators 
                                if indicator in content)
        analysis["contrarian_score"] = contrarian_matches * 0.3
        
        if contrarian_matches > 0:
            analysis["ramit_content_types"].add("contrarian")
    
    def _analyze_content_structure(self, content: str, analysis: Dict[str, Any]):
        """Analyze content structure for specific patterns"""
        # Check for step-by-step content
        step_patterns = [r"step \d+", r"\d+\.", r"first,", r"second,", r"third,"]
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in step_patterns):
            analysis["tactical_score"] += 0.5
            analysis["ramit_content_types"].add("tactical")
        
        # Check for story/case study patterns
        story_patterns = [r"let me tell you", r"here's what happened", r"student named",
                         r"client story", r"real example"]
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in story_patterns):
            analysis["case_study_score"] += 0.5
            analysis["story_score"] += 0.5
            analysis["ramit_content_types"].add("case_study")
        
        # Check for numbers and metrics
        number_patterns = [r"\$[\d,]+", r"\d+%", r"\d+ times", r"\d+ figure"]
        number_matches = sum(1 for pattern in number_patterns 
                           if re.search(pattern, content))
        if number_matches > 0:
            analysis["numbers_score"] += number_matches * 0.3
            analysis["ramit_content_types"].add("numbers")
        
        # Check for testing content
        testing_patterns = [r"test", r"experiment", r"try this", r"validate"]
        testing_matches = sum(1 for pattern in testing_patterns 
                            if re.search(pattern, content, re.IGNORECASE))
        if testing_matches > 1:
            analysis["testing_score"] += testing_matches * 0.2
            analysis["ramit_content_types"].add("testing")
    
    def _determine_primary_content_type(self, analysis: Dict[str, Any]) -> str:
        """Determine the primary content type based on scores"""
        scores = {
            "framework": analysis["framework_score"],
            "tactical": analysis["tactical_score"],
            "contrarian": analysis["contrarian_score"],
            "case_study": analysis["case_study_score"],
            "mindset": analysis["mindset_score"],
            "testing": analysis["testing_score"],
            "numbers": analysis["numbers_score"],
            "story": analysis["story_score"]
        }
        
        # Return the type with the highest score, default to "general"
        if max(scores.values()) > 0.5:
            return max(scores, key=scores.get)
        else:
            return "general"

def enhance_document_metadata(documents: List[Any]) -> List[Any]:
    """
    Enhance a list of documents with Ramit-specific metadata
    
    Args:
        documents: List of documents to enhance
        
    Returns:
        List of documents with enhanced metadata
    """
    analyzer = RamitContentAnalyzer()
    enhanced_documents = []
    
    for doc in documents:
        enhanced_metadata = analyzer.analyze_content(doc.page_content, doc.metadata)
        doc.metadata = enhanced_metadata
        enhanced_documents.append(doc)
    
    return enhanced_documents