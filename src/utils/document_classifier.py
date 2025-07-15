"""
Document Classification System for Ramit Sethi Course Content

This module analyzes PDF documents before chunking to determine their teaching context,
authority level, and content type to enable context-aware retrieval.
"""

import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from langchain.schema.document import Document
from .token_utils import count_tokens

class DocumentSourceType(Enum):
    STRUCTURED_LESSON = "structured_lesson"
    LIVE_QA = "live_qa"
    STUDENT_TEARDOWN = "student_teardown"
    BEHIND_SCENES = "behind_scenes"
    BUSINESS_MAKEOVER = "business_makeover"
    CASE_STUDY = "case_study"
    UNKNOWN = "unknown"

class TeachingContext(Enum):
    SYSTEMATIC_INSTRUCTION = "systematic_instruction"
    SITUATIONAL_ADVICE = "situational_advice"
    TROUBLESHOOTING = "troubleshooting"
    EXAMPLE_APPLICATION = "example_application"
    DIAGNOSTIC = "diagnostic"
    UNKNOWN = "unknown"

class ConfidenceLevel(Enum):
    DEFINITIVE_FRAMEWORK = "definitive_framework"
    SUGGESTED_APPROACH = "suggested_approach"
    OFF_THE_CUFF = "off_the_cuff"
    EXPLORATORY = "exploratory"
    UNKNOWN = "unknown"

@dataclass
class DocumentClassification:
    """Complete classification of a document"""
    document_source_type: DocumentSourceType
    teaching_context: TeachingContext
    confidence_level: ConfidenceLevel
    authority_score: float
    classification_confidence: float
    supporting_evidence: List[str]
    content_quality_indicators: Dict[str, float]

class DocumentClassifier:
    """
    Classifies Ramit Sethi course documents to understand their teaching context
    and authority level for enhanced retrieval.
    """
    
    def __init__(self):
        self.source_type_patterns = self._initialize_source_type_patterns()
        self.teaching_context_patterns = self._initialize_teaching_context_patterns()
        self.confidence_indicators = self._initialize_confidence_indicators()
        self.authority_indicators = self._initialize_authority_indicators()
        self.content_quality_patterns = self._initialize_content_quality_patterns()
    
    def _initialize_source_type_patterns(self) -> Dict[DocumentSourceType, List[str]]:
        """Initialize patterns for identifying document source types"""
        return {
            DocumentSourceType.STRUCTURED_LESSON: [
                r"(?i)lesson\s+\d+",
                r"(?i)module\s+\d+",
                r"(?i)chapter\s+\d+",
                r"(?i)the\s+(.+?)\s+framework",
                r"(?i)anatomy\s+of",
                r"(?i)step\s+by\s+step",
                r"(?i)here's\s+the\s+exact\s+system",
                r"(?i)components?\s+of",
                r"(?i)blueprint\s+for",
                r"(?i)complete\s+guide",
                r"(?i)systematic\s+approach",
                r"(?i)methodology",
                r"(?i)process\s+overview"
            ],
            DocumentSourceType.LIVE_QA: [
                r"(?i)q\s*&\s*a",
                r"(?i)question\s+and\s+answer",
                r"(?i)live\s+session",
                r"(?i)office\s+hours",
                r"(?i)that's\s+a\s+great\s+question",
                r"(?i)someone\s+asked",
                r"(?i)participant\s+question",
                r"(?i)student\s+question",
                r"(?i)chat\s+question",
                r"(?i)ramit:\s*",
                r"(?i)student:\s*",
                r"(?i)audience\s+member",
                r"(?i)from\s+the\s+chat",
                r"(?i)good\s+question"
            ],
            DocumentSourceType.STUDENT_TEARDOWN: [
                r"(?i)student\s+teardown",
                r"(?i)teardown\s+session",
                r"(?i)student\s+spotlight",
                r"(?i)before\s+and\s+after",
                r"(?i)student\s+transformation",
                r"(?i)real\s+student\s+example",
                r"(?i)case\s+study:\s*[A-Z]",
                r"(?i)let\s+me\s+show\s+you\s+what\s+[A-Z]\w+\s+did",
                r"(?i)student\s+story",
                r"(?i)success\s+story",
                r"(?i)transformation\s+story",
                r"(?i)one\s+of\s+our\s+students",
                r"(?i)worked\s+with\s+a\s+student"
            ],
            DocumentSourceType.BEHIND_SCENES: [
                r"(?i)behind\s+the\s+scenes",
                r"(?i)bts\s+",
                r"(?i)exclusive\s+content",
                r"(?i)bonus\s+material",
                r"(?i)deep\s+dive",
                r"(?i)advanced\s+training",
                r"(?i)insider\s+perspective",
                r"(?i)what\s+we\s+don't\s+talk\s+about",
                r"(?i)the\s+real\s+story",
                r"(?i)truth\s+about",
                r"(?i)rarely\s+discussed",
                r"(?i)confidential"
            ],
            DocumentSourceType.BUSINESS_MAKEOVER: [
                r"(?i)business\s+makeover",
                r"(?i)makeover\s+session",
                r"(?i)business\s+audit",
                r"(?i)diagnostic\s+session",
                r"(?i)let's\s+fix\s+your\s+business",
                r"(?i)business\s+review",
                r"(?i)what's\s+wrong\s+with",
                r"(?i)problems?\s+with\s+your\s+business",
                r"(?i)business\s+diagnosis",
                r"(?i)transformation\s+session"
            ],
            DocumentSourceType.CASE_STUDY: [
                r"(?i)case\s+study",
                r"(?i)real\s+example",
                r"(?i)client\s+example",
                r"(?i)actual\s+results",
                r"(?i)results\s+breakdown",
                r"(?i)how\s+[A-Z]\w+\s+made",
                r"(?i)inside\s+look\s+at",
                r"(?i)detailed\s+analysis",
                r"(?i)step\s+by\s+step\s+walkthrough"
            ]
        }
    
    def _initialize_teaching_context_patterns(self) -> Dict[TeachingContext, List[str]]:
        """Initialize patterns for identifying teaching contexts"""
        return {
            TeachingContext.SYSTEMATIC_INSTRUCTION: [
                r"(?i)here's\s+the\s+exact\s+system",
                r"(?i)framework\s+for",
                r"(?i)step\s+1\s*:",
                r"(?i)step\s+2\s*:",
                r"(?i)first,?\s+you\s+need\s+to",
                r"(?i)second,?\s+you\s+need\s+to",
                r"(?i)process\s+is\s+simple",
                r"(?i)here's\s+how\s+it\s+works",
                r"(?i)methodology\s+is",
                r"(?i)systematic\s+approach",
                r"(?i)blueprint\s+for",
                r"(?i)formula\s+for",
                r"(?i)template\s+for"
            ],
            TeachingContext.SITUATIONAL_ADVICE: [
                r"(?i)depends\s+on\s+your\s+situation",
                r"(?i)in\s+your\s+case",
                r"(?i)for\s+your\s+specific\s+situation",
                r"(?i)it\s+depends",
                r"(?i)that's\s+a\s+great\s+question",
                r"(?i)here's\s+what\s+I\s+would\s+do",
                r"(?i)my\s+recommendation\s+would\s+be",
                r"(?i)in\s+this\s+scenario",
                r"(?i)contextual\s+advice",
                r"(?i)situational\s+guidance",
                r"(?i)case\s+by\s+case",
                r"(?i)individual\s+circumstances"
            ],
            TeachingContext.TROUBLESHOOTING: [
                r"(?i)what\s+if\s+",
                r"(?i)common\s+mistake",
                r"(?i)problem\s+is",
                r"(?i)issue\s+you\s+might\s+face",
                r"(?i)here's\s+what\s+to\s+do\s+when",
                r"(?i)if\s+you're\s+struggling",
                r"(?i)solution\s+is",
                r"(?i)fix\s+for",
                r"(?i)troubleshooting",
                r"(?i)common\s+issues",
                r"(?i)problems?\s+and\s+solutions",
                r"(?i)when\s+things\s+go\s+wrong"
            ],
            TeachingContext.EXAMPLE_APPLICATION: [
                r"(?i)for\s+example",
                r"(?i)let\s+me\s+show\s+you",
                r"(?i)here's\s+an\s+example",
                r"(?i)real\s+world\s+example",
                r"(?i)practical\s+application",
                r"(?i)in\s+practice",
                r"(?i)applied\s+to",
                r"(?i)concrete\s+example",
                r"(?i)demonstration",
                r"(?i)illustration",
                r"(?i)sample\s+implementation",
                r"(?i)walkthrough"
            ],
            TeachingContext.DIAGNOSTIC: [
                r"(?i)what's\s+wrong\s+with",
                r"(?i)diagnosis\s+is",
                r"(?i)problem\s+here\s+is",
                r"(?i)root\s+cause",
                r"(?i)underlying\s+issue",
                r"(?i)let's\s+diagnose",
                r"(?i)analysis\s+shows",
                r"(?i)assessment\s+reveals",
                r"(?i)evaluation\s+indicates",
                r"(?i)symptoms\s+of",
                r"(?i)indicators\s+suggest",
                r"(?i)signs\s+point\s+to"
            ]
        }
    
    def _initialize_confidence_indicators(self) -> Dict[ConfidenceLevel, List[str]]:
        """Initialize patterns for identifying confidence levels"""
        return {
            ConfidenceLevel.DEFINITIVE_FRAMEWORK: [
                r"(?i)this\s+is\s+the\s+exact",
                r"(?i)here's\s+the\s+exact\s+system",
                r"(?i)proven\s+framework",
                r"(?i)tested\s+methodology",
                r"(?i)definitive\s+guide",
                r"(?i)guaranteed\s+approach",
                r"(?i)foolproof\s+method",
                r"(?i)never\s+fails",
                r"(?i)always\s+works",
                r"(?i)100%\s+effective",
                r"(?i)scientifically\s+proven",
                r"(?i)data\s+shows"
            ],
            ConfidenceLevel.SUGGESTED_APPROACH: [
                r"(?i)I\s+recommend",
                r"(?i)my\s+suggestion\s+is",
                r"(?i)best\s+practice\s+is",
                r"(?i)typically\s+works\s+well",
                r"(?i)generally\s+effective",
                r"(?i)usually\s+successful",
                r"(?i)tends\s+to\s+work",
                r"(?i)preferred\s+method",
                r"(?i)standard\s+approach",
                r"(?i)common\s+practice",
                r"(?i)most\s+effective",
                r"(?i)better\s+approach"
            ],
            ConfidenceLevel.OFF_THE_CUFF: [
                r"(?i)off\s+the\s+top\s+of\s+my\s+head",
                r"(?i)quick\s+thought",
                r"(?i)initial\s+reaction",
                r"(?i)gut\s+feeling",
                r"(?i)instinctively",
                r"(?i)my\s+first\s+thought",
                r"(?i)immediate\s+response",
                r"(?i)without\s+thinking\s+too\s+much",
                r"(?i)spontaneous\s+idea",
                r"(?i)stream\s+of\s+consciousness",
                r"(?i)random\s+thought",
                r"(?i)just\s+occurred\s+to\s+me"
            ],
            ConfidenceLevel.EXPLORATORY: [
                r"(?i)let's\s+explore",
                r"(?i)what\s+if\s+we",
                r"(?i)maybe\s+we\s+could",
                r"(?i)potential\s+approach",
                r"(?i)worth\s+considering",
                r"(?i)interesting\s+possibility",
                r"(?i)might\s+be\s+worth",
                r"(?i)could\s+potentially",
                r"(?i)experimental\s+approach",
                r"(?i)theoretical\s+framework",
                r"(?i)hypothesis\s+is",
                r"(?i)preliminary\s+idea"
            ]
        }
    
    def _initialize_authority_indicators(self) -> Dict[str, List[str]]:
        """Initialize patterns for calculating authority scores"""
        return {
            "high_authority": [
                r"(?i)proven\s+framework",
                r"(?i)tested\s+approach",
                r"(?i)data\s+shows",
                r"(?i)research\s+indicates",
                r"(?i)results\s+prove",
                r"(?i)evidence\s+suggests",
                r"(?i)study\s+found",
                r"(?i)analysis\s+reveals",
                r"(?i)metrics\s+show",
                r"(?i)numbers\s+demonstrate",
                r"(?i)scientific\s+method",
                r"(?i)systematically\s+tested"
            ],
            "medium_authority": [
                r"(?i)best\s+practice",
                r"(?i)recommended\s+approach",
                r"(?i)typically\s+effective",
                r"(?i)generally\s+works",
                r"(?i)standard\s+method",
                r"(?i)common\s+practice",
                r"(?i)industry\s+standard",
                r"(?i)widely\s+accepted",
                r"(?i)professional\s+opinion",
                r"(?i)expert\s+advice",
                r"(?i)experienced\s+perspective",
                r"(?i)time\s+tested"
            ],
            "low_authority": [
                r"(?i)personal\s+opinion",
                r"(?i)my\s+take\s+on",
                r"(?i)I\s+think",
                r"(?i)I\s+believe",
                r"(?i)in\s+my\s+experience",
                r"(?i)gut\s+feeling",
                r"(?i)instinct\s+tells\s+me",
                r"(?i)speculation",
                r"(?i)hypothesis",
                r"(?i)theory\s+is",
                r"(?i)might\s+be",
                r"(?i)possibly"
            ]
        }
    
    def _initialize_content_quality_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for content quality assessment"""
        return {
            "framework_density": [
                r"(?i)framework",
                r"(?i)system",
                r"(?i)process",
                r"(?i)methodology",
                r"(?i)approach",
                r"(?i)blueprint",
                r"(?i)template",
                r"(?i)formula"
            ],
            "tactical_density": [
                r"(?i)step\s+by\s+step",
                r"(?i)exact\s+script",
                r"(?i)word\s+for\s+word",
                r"(?i)copy\s+and\s+paste",
                r"(?i)template",
                r"(?i)checklist",
                r"(?i)action\s+items",
                r"(?i)implementation"
            ],
            "case_study_density": [
                r"(?i)case\s+study",
                r"(?i)real\s+example",
                r"(?i)student\s+story",
                r"(?i)success\s+story",
                r"(?i)transformation",
                r"(?i)before\s+and\s+after",
                r"(?i)results",
                r"(?i)outcome"
            ],
            "contrarian_density": [
                r"(?i)here's\s+where\s+most\s+people\s+get\s+this\s+wrong",
                r"(?i)conventional\s+wisdom\s+says",
                r"(?i)everyone\s+else\s+tells\s+you",
                r"(?i)opposite\s+of\s+what",
                r"(?i)myth\s+is",
                r"(?i)truth\s+is",
                r"(?i)reality\s+is",
                r"(?i)different\s+approach"
            ]
        }
    
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
    
    def _classify_source_type(self, content: str, filename: str) -> Tuple[DocumentSourceType, List[str]]:
        """Classify document source type based on content and filename patterns"""
        scores = {}
        evidence = []
        
        # Check filename for clues
        filename_lower = filename.lower()
        if 'qa' in filename_lower or 'q&a' in filename_lower:
            scores[DocumentSourceType.LIVE_QA] = scores.get(DocumentSourceType.LIVE_QA, 0) + 0.3
            evidence.append(f"Filename contains Q&A indicator: {filename}")
        
        if 'teardown' in filename_lower or 'student' in filename_lower:
            scores[DocumentSourceType.STUDENT_TEARDOWN] = scores.get(DocumentSourceType.STUDENT_TEARDOWN, 0) + 0.3
            evidence.append(f"Filename contains teardown/student indicator: {filename}")
        
        if 'behind' in filename_lower or 'bts' in filename_lower:
            scores[DocumentSourceType.BEHIND_SCENES] = scores.get(DocumentSourceType.BEHIND_SCENES, 0) + 0.3
            evidence.append(f"Filename contains behind scenes indicator: {filename}")
        
        # Check content patterns
        for source_type, patterns in self.source_type_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    weight = len(matches) * 0.1
                    scores[source_type] = scores.get(source_type, 0) + weight
                    evidence.append(f"Found {len(matches)} matches for {source_type.value} pattern: {pattern}")
        
        # Determine best match
        if scores:
            best_type = max(scores, key=scores.get)
            return best_type, evidence
        else:
            return DocumentSourceType.UNKNOWN, ["No clear source type patterns found"]
    
    def _classify_teaching_context(self, content: str) -> Tuple[TeachingContext, List[str]]:
        """Classify teaching context based on content patterns"""
        scores = {}
        evidence = []
        
        for context_type, patterns in self.teaching_context_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    weight = len(matches) * 0.1
                    scores[context_type] = scores.get(context_type, 0) + weight
                    evidence.append(f"Found {len(matches)} matches for {context_type.value} pattern: {pattern}")
        
        # Determine best match
        if scores:
            best_context = max(scores, key=scores.get)
            return best_context, evidence
        else:
            return TeachingContext.UNKNOWN, ["No clear teaching context patterns found"]
    
    def _classify_confidence_level(self, content: str) -> Tuple[ConfidenceLevel, List[str]]:
        """Classify confidence level based on content patterns"""
        scores = {}
        evidence = []
        
        for confidence_type, patterns in self.confidence_indicators.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    weight = len(matches) * 0.1
                    scores[confidence_type] = scores.get(confidence_type, 0) + weight
                    evidence.append(f"Found {len(matches)} matches for {confidence_type.value} pattern: {pattern}")
        
        # Determine best match
        if scores:
            best_confidence = max(scores, key=scores.get)
            return best_confidence, evidence
        else:
            return ConfidenceLevel.UNKNOWN, ["No clear confidence level patterns found"]
    
    def _calculate_authority_score(self, content: str) -> Tuple[float, List[str]]:
        """Calculate authority score based on content patterns"""
        high_authority_count = 0
        medium_authority_count = 0
        low_authority_count = 0
        evidence = []
        
        for pattern in self.authority_indicators["high_authority"]:
            matches = re.findall(pattern, content)
            if matches:
                high_authority_count += len(matches)
                evidence.append(f"High authority: {len(matches)} matches for {pattern}")
        
        for pattern in self.authority_indicators["medium_authority"]:
            matches = re.findall(pattern, content)
            if matches:
                medium_authority_count += len(matches)
                evidence.append(f"Medium authority: {len(matches)} matches for {pattern}")
        
        for pattern in self.authority_indicators["low_authority"]:
            matches = re.findall(pattern, content)
            if matches:
                low_authority_count += len(matches)
                evidence.append(f"Low authority: {len(matches)} matches for {pattern}")
        
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
                matches = re.findall(pattern, content)
                count += len(matches)
            
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

def classify_document(document: Document) -> DocumentClassification:
    """
    Convenience function to classify a single document
    
    Args:
        document: Document to classify
        
    Returns:
        DocumentClassification with complete analysis
    """
    classifier = DocumentClassifier()
    return classifier.classify_document(document)

def classify_documents(documents: List[Document]) -> List[DocumentClassification]:
    """
    Classify multiple documents
    
    Args:
        documents: List of documents to classify
        
    Returns:
        List of DocumentClassification objects
    """
    classifier = DocumentClassifier()
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
        "document_source_type": classification.document_source_type.value,
        "teaching_context": classification.teaching_context.value,
        "confidence_level": classification.confidence_level.value,
        "authority_score": classification.authority_score,
        "classification_confidence": classification.classification_confidence,
        "framework_density": classification.content_quality_indicators.get("framework_density", 0.0),
        "tactical_density": classification.content_quality_indicators.get("tactical_density", 0.0),
        "case_study_density": classification.content_quality_indicators.get("case_study_density", 0.0),
        "contrarian_density": classification.content_quality_indicators.get("contrarian_density", 0.0),
        "classification_evidence": "; ".join(classification.supporting_evidence[:5])  # First 5 pieces of evidence
    })
    
    return document