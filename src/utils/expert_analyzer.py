"""
Expert Content Analyzer

This module analyzes document chunks to identify expert-specific characteristics,
frameworks, and terminology, enriching metadata for better semantic retrieval.
Configurable for any expert through expert_config.yaml.
"""

import re
import yaml
import os
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

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
class ExpertSignature:
    """Represents a signature phrase or concept from the expert's methodology"""
    phrase: str
    content_type: ContentType
    weight: float  # How strongly this indicates the content type (0.1-1.0)
    context: str = ""  # Additional context about when this applies

class ExpertContentAnalyzer:
    """Analyzes content for expert-specific characteristics and frameworks"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the analyzer with expert configuration
        
        Args:
            config_path: Path to expert configuration YAML file
                        If None, looks for config/expert_config.yaml or EXPERT_CONFIG_PATH env var
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
        
        # Initialize components from config
        self.signatures = self._initialize_signatures()
        self.frameworks = self._initialize_frameworks()
        self.contrarian_indicators = self._initialize_contrarian_indicators()
        self.content_types = self._initialize_content_types()
        
    def _resolve_config_path(self, config_path: Optional[str]) -> str:
        """Resolve the configuration file path"""
        if config_path:
            return config_path
            
        # Check environment variable
        env_path = os.getenv('EXPERT_CONFIG_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
            
        # Default locations to check
        default_paths = [
            'config/expert_config.yaml',
            'config/examples/ramit_earnable_config.yaml',  # Fallback to Ramit config
            os.path.join(os.path.dirname(__file__), '../../config/expert_config.yaml'),
            os.path.join(os.path.dirname(__file__), '../../config/examples/ramit_earnable_config.yaml')
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
                
        raise FileNotFoundError(
            f"Expert configuration file not found. Tried: {default_paths}\\n"
            f"Please create config/expert_config.yaml or set EXPERT_CONFIG_PATH environment variable."
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """Load expert configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            # Validate required sections
            required_sections = ['expert_profile', 'content_types', 'signature_phrases']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required section '{section}' in config file")
                    
            return config
            
        except Exception as e:
            raise ValueError(f"Error loading expert configuration from {self.config_path}: {e}")
    
    def _initialize_content_types(self) -> Dict[str, float]:
        """Initialize content types from config"""
        content_types = {}
        for content_type, details in self.config.get('content_types', {}).items():
            content_types[content_type] = details.get('weight', 1.0)
        return content_types
    
    def _initialize_signatures(self) -> List[ExpertSignature]:
        """Initialize signature phrases and concepts from expert configuration"""
        signatures = []
        signature_config = self.config.get('signature_phrases', {})
        
        # Process all signature categories
        for category_name, phrases in signature_config.items():
            if isinstance(phrases, list):
                for phrase_config in phrases:
                    if isinstance(phrase_config, dict):
                        phrase = phrase_config.get('phrase', '')
                        content_type_str = phrase_config.get('content_type', 'framework')
                        weight = phrase_config.get('weight', 0.5)
                        context = phrase_config.get('context', '')
                        
                        try:
                            content_type = ContentType(content_type_str)
                            signatures.append(ExpertSignature(phrase, content_type, weight, context))
                        except ValueError:
                            # Skip invalid content types
                            continue
        
        return signatures
    
    def _initialize_frameworks(self) -> Dict[str, List[str]]:
        """Initialize expert's specific frameworks and their key components"""
        frameworks = {}
        framework_config = self.config.get('frameworks', {})
        
        for framework_name, framework_details in framework_config.items():
            if isinstance(framework_details, dict):
                keywords = framework_details.get('keywords', [])
                frameworks[framework_name] = keywords
                
        return frameworks
    
    def _initialize_contrarian_indicators(self) -> List[str]:
        """Initialize phrases that indicate contrarian takes"""
        contrarian_indicators = []
        
        # Get from signature phrases
        signature_config = self.config.get('signature_phrases', {})
        contrarian_phrases = signature_config.get('contrarian_indicators', [])
        
        for phrase_config in contrarian_phrases:
            if isinstance(phrase_config, dict):
                phrase = phrase_config.get('phrase', '')
                if phrase:
                    contrarian_indicators.append(phrase)
            elif isinstance(phrase_config, str):
                contrarian_indicators.append(phrase_config)
        
        # Add default contrarian indicators if none specified
        if not contrarian_indicators:
            contrarian_indicators = [
                "most people think", "conventional wisdom", "everyone says",
                "typical advice", "wrong approach", "don't listen to",
                "opposite of what", "counterintuitive", "surprising truth",
                "myth", "misconception", "big mistake", "dead wrong"
            ]
        
        return contrarian_indicators
    
    def analyze_content(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content and return enriched metadata with expert-specific tags
        
        Args:
            content: The text content to analyze
            metadata: Existing metadata from the document
            
        Returns:
            Enhanced metadata with expert-specific semantic tags
        """
        content_lower = content.lower()
        expert_name = self.config.get('expert_profile', {}).get('name', 'expert')
        expert_prefix = expert_name.lower().replace(' ', '_')
        
        # Initialize analysis results
        analysis = {
            f"{expert_prefix}_content_types": set(),
            f"{expert_prefix}_frameworks": set(),
            f"{expert_prefix}_signatures": [],
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
        self._analyze_signatures(content_lower, analysis, expert_prefix)
        
        # Analyze frameworks
        self._analyze_frameworks(content_lower, analysis, expert_prefix)
        
        # Analyze contrarian indicators
        self._analyze_contrarian_content(content_lower, analysis)
        
        # Analyze content structure
        self._analyze_content_structure(content, analysis, expert_prefix)
        
        # Calculate overall content classification
        primary_type = self._determine_primary_content_type(analysis)
        
        # Enhance metadata (convert sets to strings for ChromaDB compatibility)
        enhanced_metadata = metadata.copy()
        enhanced_metadata.update({
            f"{expert_prefix}_primary_type": primary_type,
            f"{expert_prefix}_content_types": ",".join(analysis[f"{expert_prefix}_content_types"]),
            f"{expert_prefix}_frameworks": ",".join(analysis[f"{expert_prefix}_frameworks"]),
            f"{expert_prefix}_signatures": ",".join(analysis[f"{expert_prefix}_signatures"]),
            f"{expert_prefix}_contrarian_score": analysis["contrarian_score"],
            f"{expert_prefix}_tactical_score": analysis["tactical_score"],
            f"{expert_prefix}_framework_score": analysis["framework_score"],
            f"{expert_prefix}_case_study_score": analysis["case_study_score"],
            f"{expert_prefix}_mindset_score": analysis["mindset_score"],
            f"{expert_prefix}_testing_score": analysis["testing_score"],
            f"{expert_prefix}_numbers_score": analysis["numbers_score"],
            f"{expert_prefix}_story_score": analysis["story_score"],
        })
        
        return enhanced_metadata
    
    def _analyze_signatures(self, content: str, analysis: Dict[str, Any], expert_prefix: str):
        """Analyze content for expert's signature phrases and concepts"""
        for signature in self.signatures:
            if re.search(signature.phrase.lower(), content, re.IGNORECASE):
                analysis[f"{expert_prefix}_signatures"].append(signature.phrase)
                analysis[f"{expert_prefix}_content_types"].add(signature.content_type.value)
                
                # Add to specific score
                score_key = f"{signature.content_type.value}_score"
                if score_key in analysis:
                    analysis[score_key] += signature.weight
    
    def _analyze_frameworks(self, content: str, analysis: Dict[str, Any], expert_prefix: str):
        """Analyze content for specific expert frameworks"""
        for framework_name, keywords in self.frameworks.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in content)
            if matches >= 2:  # Must have at least 2 framework keywords
                analysis[f"{expert_prefix}_frameworks"].add(framework_name)
                analysis["framework_score"] += matches * 0.2
    
    def _analyze_contrarian_content(self, content: str, analysis: Dict[str, Any]):
        """Analyze content for contrarian takes and perspectives"""
        contrarian_matches = sum(1 for indicator in self.contrarian_indicators 
                                if indicator.lower() in content)
        analysis["contrarian_score"] = contrarian_matches * 0.3
        
        if contrarian_matches > 0:
            expert_prefix = self.config.get('expert_profile', {}).get('name', 'expert').lower().replace(' ', '_')
            analysis[f"{expert_prefix}_content_types"].add("contrarian")
    
    def _analyze_content_structure(self, content: str, analysis: Dict[str, Any], expert_prefix: str):
        """Analyze content structure for specific patterns"""
        # Check for step-by-step content
        step_patterns = [r"step \\d+", r"\\d+\\.", r"first,", r"second,", r"third,"]
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in step_patterns):
            analysis["tactical_score"] += 0.5
            analysis[f"{expert_prefix}_content_types"].add("tactical")
        
        # Check for story/case study patterns
        story_patterns = [r"let me tell you", r"here's what happened", r"student named",
                         r"client story", r"real example"]
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in story_patterns):
            analysis["case_study_score"] += 0.5
            analysis["story_score"] += 0.5
            analysis[f"{expert_prefix}_content_types"].add("case_study")
        
        # Check for numbers and metrics
        number_patterns = [r"\\$[\\d,]+", r"\\d+%", r"\\d+ times", r"\\d+ figure"]
        number_matches = sum(1 for pattern in number_patterns 
                           if re.search(pattern, content))
        if number_matches > 0:
            analysis["numbers_score"] += number_matches * 0.3
            analysis[f"{expert_prefix}_content_types"].add("numbers")
        
        # Check for testing content
        testing_patterns = [r"test", r"experiment", r"try this", r"validate"]
        testing_matches = sum(1 for pattern in testing_patterns 
                            if re.search(pattern, content, re.IGNORECASE))
        if testing_matches > 1:
            analysis["testing_score"] += testing_matches * 0.2
            analysis[f"{expert_prefix}_content_types"].add("testing")
    
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
    
    def get_expert_info(self) -> Dict[str, Any]:
        """Get expert profile information"""
        return self.config.get('expert_profile', {})
    
    def get_available_frameworks(self) -> List[str]:
        """Get list of available frameworks"""
        return list(self.frameworks.keys())
    
    def get_content_types(self) -> List[str]:
        """Get list of available content types"""
        return list(self.content_types.keys())

def enhance_document_metadata(documents: List[Any], config_path: Optional[str] = None) -> List[Any]:
    """
    Enhance a list of documents with expert-specific metadata
    
    Args:
        documents: List of documents to enhance
        config_path: Path to expert configuration file
        
    Returns:
        List of documents with enhanced metadata
    """
    analyzer = ExpertContentAnalyzer(config_path)
    enhanced_documents = []
    
    for doc in documents:
        enhanced_metadata = analyzer.analyze_content(doc.page_content, doc.metadata)
        doc.metadata = enhanced_metadata
        enhanced_documents.append(doc)
    
    return enhanced_documents

def load_expert_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load expert configuration for use by other modules
    
    Args:
        config_path: Path to expert configuration file
        
    Returns:
        Expert configuration dictionary
    """
    analyzer = ExpertContentAnalyzer(config_path)
    return analyzer.config