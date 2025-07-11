"""
Response quality metrics for validating Ramit-enhanced RAG responses.
Measures authenticity, framework coherence, actionability, source accuracy, and coaching effectiveness.
"""

import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ..data.test_queries import (
    RAMIT_SIGNATURE_PHRASES,
    RAMIT_CONTRARIAN_INDICATORS,
    RAMIT_FRAMEWORK_TERMS,
    RAMIT_TACTICAL_LANGUAGE,
    TestQuery
)

class MetricScore(Enum):
    EXCELLENT = 5
    GOOD = 4
    AVERAGE = 3
    POOR = 2
    FAILING = 1

@dataclass
class QualityScores:
    """Container for all quality metric scores"""
    ramit_authenticity: float
    framework_coherence: float
    actionability: float
    source_accuracy: float
    coaching_effectiveness: float
    overall_score: float
    
    # Detailed breakdowns
    authenticity_details: Dict[str, Any]
    coherence_details: Dict[str, Any]
    actionability_details: Dict[str, Any]
    source_details: Dict[str, Any]
    coaching_details: Dict[str, Any]

class ResponseQualityAnalyzer:
    """Analyzes response quality across multiple dimensions"""
    
    def __init__(self):
        self.signature_phrases = RAMIT_SIGNATURE_PHRASES
        self.contrarian_indicators = RAMIT_CONTRARIAN_INDICATORS
        self.framework_terms = RAMIT_FRAMEWORK_TERMS
        self.tactical_language = RAMIT_TACTICAL_LANGUAGE
    
    def analyze_response_quality(
        self, 
        response: str, 
        query: TestQuery, 
        sources: List[Dict[str, Any]] = None,
        context: str = ""
    ) -> QualityScores:
        """Comprehensive quality analysis of a response"""
        
        # Analyze each dimension
        authenticity_score, authenticity_details = self._analyze_ramit_authenticity(response, query)
        coherence_score, coherence_details = self._analyze_framework_coherence(response, query, sources)
        actionability_score, actionability_details = self._analyze_actionability(response, query)
        source_score, source_details = self._analyze_source_accuracy(response, sources)
        coaching_score, coaching_details = self._analyze_coaching_effectiveness(response, query, context)
        
        # Calculate overall score (weighted average)
        overall_score = (
            authenticity_score * 0.25 +
            coherence_score * 0.25 +
            actionability_score * 0.20 +
            source_score * 0.15 +
            coaching_score * 0.15
        )
        
        return QualityScores(
            ramit_authenticity=authenticity_score,
            framework_coherence=coherence_score,
            actionability=actionability_score,
            source_accuracy=source_score,
            coaching_effectiveness=coaching_score,
            overall_score=overall_score,
            authenticity_details=authenticity_details,
            coherence_details=coherence_details,
            actionability_details=actionability_details,
            source_details=source_details,
            coaching_details=coaching_details
        )
    
    def _analyze_ramit_authenticity(self, response: str, query: TestQuery) -> Tuple[float, Dict[str, Any]]:
        """Analyze how authentically the response sounds like Ramit"""
        response_lower = response.lower()
        details = {
            "signature_phrases_found": [],
            "contrarian_indicators_found": [],
            "framework_terms_found": [],
            "tactical_language_found": [],
            "voice_pattern_score": 0.0,
            "terminology_score": 0.0,
            "personality_score": 0.0
        }
        
        # Check for signature phrases
        signature_count = 0
        for phrase in self.signature_phrases:
            if phrase.lower() in response_lower:
                details["signature_phrases_found"].append(phrase)
                signature_count += 1
        
        # Check for contrarian indicators (if expected)
        contrarian_count = 0
        if query.should_be_contrarian:
            for indicator in self.contrarian_indicators:
                if indicator.lower() in response_lower:
                    details["contrarian_indicators_found"].append(indicator)
                    contrarian_count += 1
        
        # Check for framework terminology
        framework_count = 0
        for term in self.framework_terms:
            if term.lower() in response_lower:
                details["framework_terms_found"].append(term)
                framework_count += 1
        
        # Check for tactical language (if expected)
        tactical_count = 0
        if query.should_be_tactical:
            for phrase in self.tactical_language:
                if phrase.lower() in response_lower:
                    details["tactical_language_found"].append(phrase)
                    tactical_count += 1
        
        # Score voice patterns
        voice_score = min(1.0, signature_count * 0.3)  # Up to 1.0 for signature phrases
        if query.should_be_contrarian:
            voice_score += min(0.5, contrarian_count * 0.25)  # Bonus for contrarian style
        if query.should_be_tactical:
            voice_score += min(0.5, tactical_count * 0.2)  # Bonus for tactical language
        
        details["voice_pattern_score"] = voice_score
        
        # Score terminology usage
        terminology_score = min(1.0, framework_count * 0.1)  # Framework terms
        details["terminology_score"] = terminology_score
        
        # Score personality indicators
        personality_indicators = [
            "let me tell you", "here's the thing", "look", "listen",
            "the truth is", "here's what", "i'll be direct", "no-nonsense"
        ]
        personality_count = sum(1 for indicator in personality_indicators 
                               if indicator in response_lower)
        personality_score = min(1.0, personality_count * 0.2)
        details["personality_score"] = personality_score
        
        # Calculate final authenticity score
        authenticity_score = (voice_score * 0.5 + terminology_score * 0.3 + personality_score * 0.2) * 5
        
        return authenticity_score, details
    
    def _analyze_framework_coherence(
        self, 
        response: str, 
        query: TestQuery, 
        sources: List[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """Analyze how well the response represents Ramit's frameworks"""
        details = {
            "expected_frameworks_mentioned": [],
            "unexpected_frameworks_mentioned": [],
            "framework_connections": [],
            "accuracy_score": 0.0,
            "completeness_score": 0.0,
            "connection_score": 0.0
        }
        
        response_lower = response.lower()
        
        # Check for expected frameworks
        expected_mentioned = 0
        for framework in query.framework_expectations:
            framework_clean = framework.replace("_", " ")
            if framework_clean in response_lower:
                details["expected_frameworks_mentioned"].append(framework)
                expected_mentioned += 1
        
        # Check for framework connections
        connection_indicators = [
            "connects to", "builds on", "leads to", "depends on",
            "follows from", "relates to", "part of", "within"
        ]
        connection_count = sum(1 for indicator in connection_indicators 
                              if indicator in response_lower)
        
        # Look for systematic thinking
        systematic_indicators = [
            "framework", "system", "process", "methodology", 
            "approach", "structure", "components", "elements"
        ]
        systematic_count = sum(1 for indicator in systematic_indicators 
                              if indicator in response_lower)
        
        # Calculate scores
        if query.framework_expectations:
            accuracy_score = expected_mentioned / len(query.framework_expectations)
        else:
            accuracy_score = 1.0 if systematic_count > 0 else 0.5
        
        completeness_score = min(1.0, systematic_count * 0.2)
        connection_score = min(1.0, connection_count * 0.3)
        
        details["accuracy_score"] = accuracy_score
        details["completeness_score"] = completeness_score  
        details["connection_score"] = connection_score
        
        # Calculate final coherence score
        coherence_score = (accuracy_score * 0.5 + completeness_score * 0.3 + connection_score * 0.2) * 5
        
        return coherence_score, details
    
    def _analyze_actionability(self, response: str, query: TestQuery) -> Tuple[float, Dict[str, Any]]:
        """Analyze how actionable and implementable the guidance is"""
        details = {
            "specific_steps_found": [],
            "scripts_provided": False,
            "concrete_examples": [],
            "implementation_guidance": False,
            "specificity_score": 0.0,
            "implementability_score": 0.0
        }
        
        response_lower = response.lower()
        
        # Look for specific steps
        step_patterns = [
            r"step \d+", r"first[,:]", r"second[,:]", r"third[,:]",
            r"next[,:]", r"then[,:]", r"finally[,:]"
        ]
        steps_found = []
        for pattern in step_patterns:
            matches = re.findall(pattern, response_lower)
            steps_found.extend(matches)
        
        details["specific_steps_found"] = steps_found
        
        # Check for scripts or templates
        script_indicators = ["script", "template", "copy and paste", "exact language", "say this"]
        scripts_provided = any(indicator in response_lower for indicator in script_indicators)
        details["scripts_provided"] = scripts_provided
        
        # Look for concrete examples
        example_indicators = ["for example", "here's how", "like this", "such as"]
        examples_count = sum(1 for indicator in example_indicators if indicator in response_lower)
        details["concrete_examples"] = examples_count
        
        # Check for implementation guidance
        implementation_indicators = [
            "implement", "apply", "put into practice", "take action",
            "do this", "start by", "begin with"
        ]
        implementation_guidance = any(indicator in response_lower for indicator in implementation_indicators)
        details["implementation_guidance"] = implementation_guidance
        
        # Calculate scores
        specificity_score = min(1.0, len(steps_found) * 0.2 + (1.0 if scripts_provided else 0.0) * 0.3)
        implementability_score = min(1.0, examples_count * 0.2 + (1.0 if implementation_guidance else 0.0) * 0.4)
        
        details["specificity_score"] = specificity_score
        details["implementability_score"] = implementability_score
        
        # Adjust expectations based on query type
        expected_actionability = 1.0 if query.should_be_tactical else 0.6
        
        actionability_score = (specificity_score * 0.6 + implementability_score * 0.4) * 5
        
        # Scale based on expectations
        if not query.should_be_tactical:
            actionability_score = max(actionability_score, 2.5)  # Minimum score for non-tactical queries
        
        return actionability_score, details
    
    def _analyze_source_accuracy(
        self, 
        response: str, 
        sources: List[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """Analyze how well the response is supported by retrieved sources"""
        details = {
            "sources_referenced": 0,
            "source_alignment": 0.0,
            "ramit_content_ratio": 0.0,
            "content_accuracy": 0.0
        }
        
        if not sources:
            return 3.0, details  # Neutral score if no sources provided
        
        details["sources_referenced"] = len(sources)
        
        # Calculate Ramit content ratio
        ramit_sources = sum(1 for source in sources 
                           if source.get("ramit_type", "general") != "general")
        ramit_ratio = ramit_sources / len(sources) if sources else 0.0
        details["ramit_content_ratio"] = ramit_ratio
        
        # Check alignment with source content
        response_words = set(response.lower().split())
        source_alignment_scores = []
        
        for source in sources:
            source_content = source.get("content", "").lower()
            source_words = set(source_content.split())
            
            # Calculate word overlap
            if source_words:
                overlap = len(response_words & source_words) / len(source_words)
                source_alignment_scores.append(overlap)
        
        avg_alignment = sum(source_alignment_scores) / len(source_alignment_scores) if source_alignment_scores else 0.0
        details["source_alignment"] = avg_alignment
        
        # Calculate content accuracy (simplified heuristic)
        content_accuracy = min(1.0, avg_alignment * 2)  # Scale alignment to accuracy
        details["content_accuracy"] = content_accuracy
        
        # Calculate final source accuracy score
        source_score = (ramit_ratio * 0.4 + avg_alignment * 0.4 + content_accuracy * 0.2) * 5
        
        return source_score, details
    
    def _analyze_coaching_effectiveness(
        self, 
        response: str, 
        query: TestQuery, 
        context: str = ""
    ) -> Tuple[float, Dict[str, Any]]:
        """Analyze how effectively the response coaches the user forward"""
        details = {
            "pushes_thinking": False,
            "asks_questions": [],
            "challenges_assumptions": False,
            "provides_next_steps": False,
            "personalization": 0.0,
            "engagement_score": 0.0
        }
        
        response_lower = response.lower()
        
        # Check if response pushes thinking forward
        thinking_indicators = [
            "have you considered", "what if", "think about", "consider this",
            "here's what most people miss", "the real question is"
        ]
        pushes_thinking = any(indicator in response_lower for indicator in thinking_indicators)
        details["pushes_thinking"] = pushes_thinking
        
        # Look for coaching questions
        question_patterns = [
            r"what [^?]+\?", r"how [^?]+\?", r"why [^?]+\?", 
            r"when [^?]+\?", r"where [^?]+\?"
        ]
        questions_found = []
        for pattern in question_patterns:
            matches = re.findall(pattern, response_lower)
            questions_found.extend(matches)
        
        details["asks_questions"] = questions_found
        
        # Check for assumption challenging
        challenge_indicators = [
            "assumption", "belief", "might be wrong", "reconsider",
            "challenge", "question", "think differently"
        ]
        challenges_assumptions = any(indicator in response_lower for indicator in challenge_indicators)
        details["challenges_assumptions"] = challenges_assumptions
        
        # Look for next steps
        next_step_indicators = [
            "next step", "what's next", "now", "moving forward",
            "your homework", "action item", "try this"
        ]
        provides_next_steps = any(indicator in response_lower for indicator in next_step_indicators)
        details["provides_next_steps"] = provides_next_steps
        
        # Check for personalization
        personal_indicators = [
            "you", "your", "based on your", "in your case",
            "for your situation", "given your"
        ]
        personalization_count = sum(1 for indicator in personal_indicators if indicator in response_lower)
        personalization_score = min(1.0, personalization_count * 0.1)
        details["personalization"] = personalization_score
        
        # Calculate engagement score
        engagement_elements = [
            pushes_thinking, bool(questions_found), challenges_assumptions,
            provides_next_steps, personalization_score > 0.3
        ]
        engagement_score = sum(engagement_elements) / len(engagement_elements)
        details["engagement_score"] = engagement_score
        
        # Calculate final coaching effectiveness score
        coaching_score = (
            (1.0 if pushes_thinking else 0.0) * 0.3 +
            min(1.0, len(questions_found) * 0.2) * 0.2 +
            (1.0 if challenges_assumptions else 0.0) * 0.2 +
            (1.0 if provides_next_steps else 0.0) * 0.2 +
            personalization_score * 0.1
        ) * 5
        
        return coaching_score, details

class QualityMetricsAggregator:
    """Aggregates and analyzes quality metrics across multiple responses"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, query: TestQuery, scores: QualityScores, response: str):
        """Add a quality analysis result"""
        self.results.append({
            "query": query,
            "scores": scores,
            "response": response,
            "timestamp": None  # Could add timestamp if needed
        })
    
    def get_category_averages(self) -> Dict[str, Dict[str, float]]:
        """Get average scores by query category"""
        category_scores = {}
        
        for result in self.results:
            category = result["query"].category
            if category not in category_scores:
                category_scores[category] = []
            
            category_scores[category].append(result["scores"])
        
        # Calculate averages
        averages = {}
        for category, scores_list in category_scores.items():
            if scores_list:
                averages[category] = {
                    "ramit_authenticity": sum(s.ramit_authenticity for s in scores_list) / len(scores_list),
                    "framework_coherence": sum(s.framework_coherence for s in scores_list) / len(scores_list),
                    "actionability": sum(s.actionability for s in scores_list) / len(scores_list),
                    "source_accuracy": sum(s.source_accuracy for s in scores_list) / len(scores_list),
                    "coaching_effectiveness": sum(s.coaching_effectiveness for s in scores_list) / len(scores_list),
                    "overall_score": sum(s.overall_score for s in scores_list) / len(scores_list),
                    "count": len(scores_list)
                }
        
        return averages
    
    def get_overall_metrics(self) -> Dict[str, float]:
        """Get overall metrics across all responses"""
        if not self.results:
            return {}
        
        all_scores = [result["scores"] for result in self.results]
        
        return {
            "ramit_authenticity": sum(s.ramit_authenticity for s in all_scores) / len(all_scores),
            "framework_coherence": sum(s.framework_coherence for s in all_scores) / len(all_scores),
            "actionability": sum(s.actionability for s in all_scores) / len(all_scores),
            "source_accuracy": sum(s.source_accuracy for s in all_scores) / len(all_scores),
            "coaching_effectiveness": sum(s.coaching_effectiveness for s in all_scores) / len(all_scores),
            "overall_score": sum(s.overall_score for s in all_scores) / len(all_scores),
            "total_responses": len(all_scores)
        }
    
    def get_failing_responses(self, threshold: float = 2.5) -> List[Dict[str, Any]]:
        """Get responses that scored below threshold"""
        failing = []
        for result in self.results:
            if result["scores"].overall_score < threshold:
                failing.append({
                    "query": result["query"].query,
                    "category": result["query"].category,
                    "overall_score": result["scores"].overall_score,
                    "weak_areas": self._identify_weak_areas(result["scores"]),
                    "response_preview": result["response"][:200] + "..."
                })
        
        return failing
    
    def _identify_weak_areas(self, scores: QualityScores) -> List[str]:
        """Identify which metrics scored poorly"""
        weak_areas = []
        threshold = 2.5
        
        if scores.ramit_authenticity < threshold:
            weak_areas.append("ramit_authenticity")
        if scores.framework_coherence < threshold:
            weak_areas.append("framework_coherence")
        if scores.actionability < threshold:
            weak_areas.append("actionability")
        if scores.source_accuracy < threshold:
            weak_areas.append("source_accuracy")
        if scores.coaching_effectiveness < threshold:
            weak_areas.append("coaching_effectiveness")
        
        return weak_areas
    
    def export_results(self, filepath: str):
        """Export results to JSON file"""
        export_data = []
        for result in self.results:
            export_data.append({
                "query": asdict(result["query"]),
                "scores": asdict(result["scores"]),
                "response": result["response"]
            })
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)