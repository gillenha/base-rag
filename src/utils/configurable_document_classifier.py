"""
Configurable Document Classification System

This module analyzes PDF documents before chunking to determine their teaching context,
authority level, and content type to enable context-aware retrieval. Configurable for
any expert through expert_config.yaml.
"""

import re
import yaml
import os
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from langchain.schema.document import Document
from .token_utils import count_tokens
from .expert_analyzer import load_expert_config

class DocumentSourceType(Enum):
    """Dynamically populated from config"""
    UNKNOWN = "unknown"

class TeachingContext(Enum):
    """Dynamically populated from config"""
    UNKNOWN = "unknown"

class ConfidenceLevel(Enum):
    """Dynamically populated from config"""
    UNKNOWN = "unknown"

@dataclass
class DocumentClassification:
    """Complete classification of a document"""
    document_source_type: str
    teaching_context: str
    confidence_level: str
    authority_score: float
    classification_confidence: float
    supporting_evidence: List[str]
    content_quality_indicators: Dict[str, float]

class ConfigurableDocumentClassifier:
    """
    Classifies expert course documents to understand their teaching context
    and authority level for enhanced retrieval. Configurable through expert config.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize classifier with expert configuration
        
        Args:
            config_path: Path to expert configuration file
        """
        self.config = load_expert_config(config_path)
        self.expert_name = self.config.get('expert_profile', {}).get('name', 'Expert')
        
        # Initialize patterns from config
        self.source_type_patterns = self._initialize_source_type_patterns()
        self.teaching_context_patterns = self._initialize_teaching_context_patterns()
        self.confidence_indicators = self._initialize_confidence_indicators()
        self.authority_indicators = self._initialize_authority_indicators()
        self.content_quality_patterns = self._initialize_content_quality_patterns()
    
    def _initialize_source_type_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for identifying document source types from config"""
        patterns = {}
        document_types = self.config.get('document_types', {})
        
        for doc_type, type_config in document_types.items():
            if isinstance(type_config, dict):
                type_patterns = type_config.get('patterns', [])
                patterns[doc_type] = type_patterns
        
        # Add unknown as fallback
        if 'unknown' not in patterns:
            patterns['unknown'] = []
            
        return patterns
    
    def _initialize_teaching_context_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for identifying teaching contexts from config"""
        patterns = {}
        teaching_contexts = self.config.get('teaching_contexts', {})
        
        for context_type, context_config in teaching_contexts.items():
            if isinstance(context_config, dict):
                context_patterns = context_config.get('patterns', [])
                patterns[context_type] = context_patterns
        
        # Add unknown as fallback
        if 'unknown' not in patterns:
            patterns['unknown'] = []
            
        return patterns
    
    def _initialize_confidence_indicators(self) -> Dict[str, List[str]]:
        """Initialize patterns for identifying confidence levels from config"""
        patterns = {}
        authority_levels = self.config.get('authority_levels', {})
        
        for confidence_type, confidence_config in authority_levels.items():
            if isinstance(confidence_config, dict):
                confidence_patterns = confidence_config.get('patterns', [])
                patterns[confidence_type] = confidence_patterns
        
        # Add unknown as fallback
        if 'unknown' not in patterns:
            patterns['unknown'] = []
            
        return patterns
    
    def _initialize_authority_indicators(self) -> Dict[str, List[str]]:
        """Initialize patterns for calculating authority scores from config"""
        # Map authority levels to their patterns
        authority_indicators = {
            "high_authority": [],
            "medium_authority": [],
            "low_authority": []
        }
        
        authority_levels = self.config.get('authority_levels', {})
        
        # Map config authority levels to our standard categories
        authority_mapping = {
            'high_authority': 'high_authority',
            'medium_authority': 'medium_authority', 
            'low_authority': 'low_authority',
            'definitive_framework': 'high_authority',
            'suggested_approach': 'medium_authority',
            'off_the_cuff': 'low_authority',
            'exploratory': 'low_authority'
        }
        
        for level_name, level_config in authority_levels.items():
            if isinstance(level_config, dict):
                patterns = level_config.get('patterns', [])
                mapped_category = authority_mapping.get(level_name, 'medium_authority')
                authority_indicators[mapped_category].extend(patterns)
        
        return authority_indicators
    
    def _initialize_content_quality_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for content quality assessment"""
        # Use content types from expert config for quality assessment
        quality_patterns = {}
        content_types = self.config.get('content_types', {})
        
        # Map content types to search patterns
        for content_type in content_types.keys():
            if content_type == 'framework':
                quality_patterns['framework_density'] = [
                    "framework", "system", "process", "methodology", 
                    "approach", "blueprint", "template", "formula"
                ]
            elif content_type == 'tactical':
                quality_patterns['tactical_density'] = [
                    "step by step", "exact script", "word for word",
                    "copy and paste", "template", "checklist", 
                    "action items", "implementation"
                ]
            elif content_type == 'case_study':
                quality_patterns['case_study_density'] = [
                    "case study", "real example", "student story",
                    "success story", "transformation", "before and after",
                    "results", "outcome"
                ]
            elif content_type == 'contrarian':
                quality_patterns['contrarian_density'] = [
                    "here's where most people get this wrong",
                    "conventional wisdom says", "everyone else tells you",
                    "opposite of what", "myth is", "truth is",
                    "reality is", "different approach"
                ]
        
        return quality_patterns
    
    def classify_document(self, document: Document) -> DocumentClassification:
        """
        Classify a document to determine its source type, teaching context, and authority level
        
        Args:
            document: Document to classify
            
        Returns:
            DocumentClassification with complete analysis
        """
        content = document.page_content.lower()
        filename = document.metadata.get('filename', '')
        
        # Analyze document source type
        source_type, source_evidence = self._classify_source_type(content, filename)
        
        # Analyze teaching context
        teaching_context, context_evidence = self._classify_teaching_context(content)
        
        # Analyze confidence level
        confidence_level, confidence_evidence = self._classify_confidence_level(content)
        
        # Calculate authority score
        authority_score, authority_evidence = self._calculate_authority_score(content)
        
        # Assess content quality indicators
        quality_indicators = self._assess_content_quality(content)
        
        # Calculate overall classification confidence
        classification_confidence = self._calculate_classification_confidence(
            source_evidence, context_evidence, confidence_evidence, authority_evidence
        )
        
        # Combine all evidence
        all_evidence = source_evidence + context_evidence + confidence_evidence + authority_evidence
        
        return DocumentClassification(
            document_source_type=source_type,
            teaching_context=teaching_context,
            confidence_level=confidence_level,
            authority_score=authority_score,
            classification_confidence=classification_confidence,
            supporting_evidence=all_evidence,
            content_quality_indicators=quality_indicators
        )
    
    def _classify_source_type(self, content: str, filename: str) -> Tuple[str, List[str]]:
        """Classify document source type based on content and filename patterns"""
        scores = {}
        evidence = []
        
        # Check filename for clues based on config patterns
        filename_lower = filename.lower()
        for source_type, patterns in self.source_type_patterns.items():
            for pattern in patterns:
                # Simple keyword matching for filename
                pattern_keywords = re.findall(r'\\w+', pattern.lower())
                if any(keyword in filename_lower for keyword in pattern_keywords):
                    scores[source_type] = scores.get(source_type, 0) + 0.3
                    evidence.append(f"Filename contains {source_type} indicator: {filename}")
                    break
        
        # Check content patterns
        for source_type, patterns in self.source_type_patterns.items():
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        weight = len(matches) * 0.1
                        scores[source_type] = scores.get(source_type, 0) + weight
                        evidence.append(f"Found {len(matches)} matches for {source_type} pattern: {pattern}")
                except re.error:
                    # Skip invalid regex patterns
                    continue
        
        # Determine best match
        if scores:
            best_type = max(scores, key=scores.get)
            return best_type, evidence
        else:
            return "unknown", ["No clear source type patterns found"]
    
    def _classify_teaching_context(self, content: str) -> Tuple[str, List[str]]:
        """Classify teaching context based on content patterns"""
        scores = {}
        evidence = []
        
        for context_type, patterns in self.teaching_context_patterns.items():
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        weight = len(matches) * 0.1
                        scores[context_type] = scores.get(context_type, 0) + weight
                        evidence.append(f"Found {len(matches)} matches for {context_type} pattern: {pattern}")
                except re.error:
                    # Skip invalid regex patterns
                    continue
        
        # Determine best match
        if scores:
            best_context = max(scores, key=scores.get)
            return best_context, evidence
        else:
            return "unknown", ["No clear teaching context patterns found"]
    
    def _classify_confidence_level(self, content: str) -> Tuple[str, List[str]]:
        """Classify confidence level based on content patterns"""
        scores = {}
        evidence = []
        
        for confidence_type, patterns in self.confidence_indicators.items():
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        weight = len(matches) * 0.1
                        scores[confidence_type] = scores.get(confidence_type, 0) + weight
                        evidence.append(f"Found {len(matches)} matches for {confidence_type} pattern: {pattern}")
                except re.error:
                    # Skip invalid regex patterns
                    continue
        
        # Determine best match
        if scores:
            best_confidence = max(scores, key=scores.get)
            return best_confidence, evidence
        else:
            return "unknown", ["No clear confidence level patterns found"]
    
    def _calculate_authority_score(self, content: str) -> Tuple[float, List[str]]:
        """Calculate authority score based on content patterns"""
        high_authority_count = 0
        medium_authority_count = 0
        low_authority_count = 0
        evidence = []
        
        for pattern in self.authority_indicators.get("high_authority", []):
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    high_authority_count += len(matches)
                    evidence.append(f"High authority: {len(matches)} matches for {pattern}")
            except re.error:
                continue
        
        for pattern in self.authority_indicators.get("medium_authority", []):
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    medium_authority_count += len(matches)
                    evidence.append(f"Medium authority: {len(matches)} matches for {pattern}")
            except re.error:
                continue
        
        for pattern in self.authority_indicators.get("low_authority", []):
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    low_authority_count += len(matches)
                    evidence.append(f"Low authority: {len(matches)} matches for {pattern}")
            except re.error:
                continue
        
        # Calculate weighted score
        total_indicators = high_authority_count + medium_authority_count + low_authority_count
        if total_indicators == 0:
            return 0.5, ["No authority indicators found - default medium authority"]
        
        authority_score = (
            (high_authority_count * 1.0) +
            (medium_authority_count * 0.6) +
            (low_authority_count * 0.2)
        ) / total_indicators
        
        return authority_score, evidence
    
    def _assess_content_quality(self, content: str) -> Dict[str, float]:
        """Assess content quality using various indicators"""
        quality_scores = {}
        
        # Calculate content length for normalization
        content_length = len(content.split())
        
        for quality_type, patterns in self.content_quality_patterns.items():
            count = 0
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    count += len(matches)
                except re.error:
                    continue
            
            # Normalize by content length
            if content_length > 0:
                density = count / content_length * 100  # Percentage
                quality_scores[quality_type] = min(1.0, density * 10)  # Cap at 1.0
            else:
                quality_scores[quality_type] = 0.0
        
        return quality_scores
    
    def _calculate_classification_confidence(self, *evidence_lists) -> float:
        """Calculate overall confidence in the classification"""
        total_evidence = sum(len(evidence) for evidence in evidence_lists)
        
        if total_evidence == 0:
            return 0.1  # Very low confidence
        elif total_evidence < 5:
            return 0.3  # Low confidence
        elif total_evidence < 10:
            return 0.6  # Medium confidence
        elif total_evidence < 20:
            return 0.8  # High confidence
        else:
            return 0.9  # Very high confidence

def classify_document(document: Document, config_path: Optional[str] = None) -> DocumentClassification:
    """
    Convenience function to classify a single document
    
    Args:
        document: Document to classify
        config_path: Path to expert configuration file
        
    Returns:
        DocumentClassification with complete analysis
    """
    classifier = ConfigurableDocumentClassifier(config_path)
    return classifier.classify_document(document)

def classify_documents(documents: List[Document], config_path: Optional[str] = None) -> List[DocumentClassification]:
    """
    Classify multiple documents
    
    Args:
        documents: List of documents to classify
        config_path: Path to expert configuration file
        
    Returns:
        List of DocumentClassification objects
    """
    classifier = ConfigurableDocumentClassifier(config_path)
    return [classifier.classify_document(doc) for doc in documents]

def add_document_classification_metadata(document: Document, classification: DocumentClassification) -> Document:
    """
    Add classification metadata to a document
    
    Args:
        document: Document to enhance
        classification: Classification to add
        
    Returns:
        Document with enhanced metadata
    """
    document.metadata.update({
        "document_source_type": classification.document_source_type,
        "teaching_context": classification.teaching_context,
        "confidence_level": classification.confidence_level,
        "authority_score": classification.authority_score,
        "classification_confidence": classification.classification_confidence,
        "framework_density": classification.content_quality_indicators.get("framework_density", 0.0),
        "tactical_density": classification.content_quality_indicators.get("tactical_density", 0.0),
        "case_study_density": classification.content_quality_indicators.get("case_study_density", 0.0),
        "contrarian_density": classification.content_quality_indicators.get("contrarian_density", 0.0),
        "classification_evidence": "; ".join(classification.supporting_evidence[:5])  # First 5 pieces of evidence
    })
    
    return document