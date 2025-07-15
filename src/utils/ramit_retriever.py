"""
Ramit-Enhanced Retriever

Custom retriever that uses Ramit-specific metadata and document classification
to improve semantic matching and prioritize content that matches Ramit's 
distinctive methodology and teaching context.
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from pydantic import Field
import re

class RamitEnhancedRetriever(BaseRetriever):
    """
    Enhanced retriever that uses Ramit-specific metadata and document classification
    to improve search results by prioritizing content that matches Ramit's frameworks,
    approaches, and teaching context.
    """
    
    vector_store: Any = Field()
    ramit_keywords: Dict[str, List[str]] = Field(default_factory=dict)
    query_type_priorities: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    def __init__(self, vector_store, **kwargs):
        super().__init__(
            vector_store=vector_store, 
            ramit_keywords=self._initialize_ramit_keywords(),
            query_type_priorities=self._initialize_query_type_priorities(),
            **kwargs
        )
        
    def _initialize_ramit_keywords(self) -> Dict[str, List[str]]:
        """Initialize keyword mappings for different types of queries"""
        return {
            "first_sale": [
                "authentic selling", "sales call", "first client", "first sale",
                "closing", "objection handling", "sales process"
            ],
            "customer_research": [
                "customer research", "mind reading", "customer interviews",
                "customer needs", "dream outcome", "biggest challenge"
            ],
            "pricing": [
                "pricing", "rates", "charge", "money", "value", "investment"
            ],
            "offers": [
                "offer", "irresistible", "positioning", "guarantee", "bonuses"
            ],
            "frameworks": [
                "framework", "system", "process", "step by step", "methodology"
            ],
            "contrarian": [
                "wrong", "myth", "conventional wisdom", "different", "opposite"
            ],
            "testing": [
                "test", "validate", "experiment", "try", "iterate"
            ]
        }
    
    def _classify_query(self, query: str) -> List[str]:
        """Classify the query to understand what type of Ramit content to prioritize"""
        query_lower = query.lower()
        matching_categories = []
        
        for category, keywords in self.ramit_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                matching_categories.append(category)
        
        return matching_categories
    
    def _initialize_query_type_priorities(self) -> Dict[str, Dict[str, float]]:
        """Initialize priority weights for different query types and document contexts"""
        return {
            "foundational": {
                "structured_lesson": 1.0,
                "systematic_instruction": 1.0,
                "definitive_framework": 1.0,
                "live_qa": 0.4,
                "situational_advice": 0.3,
                "off_the_cuff": 0.2
            },
            "specific_problems": {
                "live_qa": 1.0,
                "situational_advice": 1.0,
                "troubleshooting": 1.0,
                "structured_lesson": 0.6,
                "systematic_instruction": 0.5,
                "definitive_framework": 0.7
            },
            "examples": {
                "student_teardown": 1.0,
                "case_study": 1.0,
                "example_application": 1.0,
                "behind_scenes": 0.8,
                "business_makeover": 0.8,
                "structured_lesson": 0.4
            },
            "systematic": {
                "structured_lesson": 1.0,
                "systematic_instruction": 1.0,
                "definitive_framework": 1.0,
                "suggested_approach": 0.8,
                "live_qa": 0.3,
                "off_the_cuff": 0.2
            }
        }
    
    def _classify_query_intent(self, query: str) -> str:
        """Classify query intent for context-aware prioritization"""
        query_lower = query.lower()
        
        # Foundational questions
        foundational_indicators = [
            "how do i", "what is the", "explain", "framework for", "system for",
            "process for", "steps to", "guide to", "introduction to", "basics of"
        ]
        if any(indicator in query_lower for indicator in foundational_indicators):
            return "foundational"
        
        # Specific problems
        problem_indicators = [
            "problem", "issue", "stuck", "struggling", "not working", "failing",
            "what should i do", "help with", "fix", "solve", "troubleshoot"
        ]
        if any(indicator in query_lower for indicator in problem_indicators):
            return "specific_problems"
        
        # Examples and case studies
        example_indicators = [
            "example", "case study", "show me", "real world", "success story",
            "student story", "how did", "what happened", "results"
        ]
        if any(indicator in query_lower for indicator in example_indicators):
            return "examples"
        
        # Systematic approaches
        systematic_indicators = [
            "systematic", "methodology", "complete", "comprehensive", "step by step",
            "exact process", "blueprint", "template", "checklist"
        ]
        if any(indicator in query_lower for indicator in systematic_indicators):
            return "systematic"
        
        # Default to foundational
        return "foundational"
    
    def _calculate_ramit_relevance_score(self, doc: Document, query_categories: List[str], query_intent: str) -> float:
        """Calculate relevance score based on Ramit-specific metadata and document classification"""
        metadata = doc.metadata
        score = 0.0
        
        # Base score from Ramit content types
        primary_type = metadata.get("ramit_primary_type", "general")
        if primary_type != "general":
            score += 0.3
            
        # Context-aware scoring based on document classification
        document_source_type = metadata.get("document_source_type", "unknown")
        teaching_context = metadata.get("teaching_context", "unknown")
        confidence_level = metadata.get("confidence_level", "unknown")
        authority_score = metadata.get("authority_score", 0.5)
        
        # Apply query intent priorities
        priorities = self.query_type_priorities.get(query_intent, {})
        
        # Boost based on document source type match
        source_priority = priorities.get(document_source_type, 0.5)
        score += source_priority * 0.4
        
        # Boost based on teaching context match
        context_priority = priorities.get(teaching_context, 0.5)
        score += context_priority * 0.3
        
        # Boost based on confidence level match
        confidence_priority = priorities.get(confidence_level, 0.5)
        score += confidence_priority * 0.2
        
        # Authority score boost
        score += authority_score * 0.3
        
        # Classification confidence boost
        classification_confidence = metadata.get("classification_confidence", 0.5)
        score += classification_confidence * 0.1
        
        # Content quality indicators
        framework_density = metadata.get("framework_density", 0.0)
        tactical_density = metadata.get("tactical_density", 0.0)
        case_study_density = metadata.get("case_study_density", 0.0)
        contrarian_density = metadata.get("contrarian_density", 0.0)
        
        # Boost based on query categories and content density
        for category in query_categories:
            if category == "first_sale" and any(f in metadata.get("ramit_frameworks", "") for f in ["authentic_selling"]):
                score += 0.5
            elif category == "customer_research" and "customer_research" in metadata.get("ramit_frameworks", ""):
                score += 0.5
            elif category == "offers" and "winning_offer" in metadata.get("ramit_frameworks", ""):
                score += 0.5
            elif category == "contrarian":
                score += contrarian_density * 0.5
            elif category == "frameworks":
                score += framework_density * 0.5
            elif category == "testing" and tactical_density > 0.3:
                score += tactical_density * 0.3
        
        # Boost for high Ramit scores (legacy support)
        contrarian_score = metadata.get("ramit_contrarian_score", 0)
        tactical_score = metadata.get("ramit_tactical_score", 0)
        framework_score = metadata.get("ramit_framework_score", 0)
        case_study_score = metadata.get("ramit_case_study_score", 0)
        
        score += contrarian_score * 0.15
        score += tactical_score * 0.15
        score += framework_score * 0.15
        score += case_study_score * 0.1
        
        # Boost for specific Ramit signatures
        ramit_signatures = metadata.get("ramit_signatures", "").split(",") if metadata.get("ramit_signatures") else []
        signature_boost = len([s for s in ramit_signatures if s.strip()]) * 0.1
        score += min(signature_boost, 0.3)  # Cap at 0.3
        
        return score
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """Retrieve documents with context-aware Ramit-enhanced scoring"""
        
        # Get initial results from vector search (default k=5, get more to rerank)
        k = 5
        initial_results = self.vector_store.similarity_search(query, k=k*2)  # Get more to rerank
        
        # Classify the query
        query_categories = self._classify_query(query)
        query_intent = self._classify_query_intent(query)
        
        # Calculate Ramit relevance scores and rerank
        scored_results = []
        for doc in initial_results:
            ramit_score = self._calculate_ramit_relevance_score(doc, query_categories, query_intent)
            scored_results.append((doc, ramit_score))
        
        # Sort by Ramit relevance score (descending)
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Debug logging for context-aware retrieval
        if scored_results:
            print(f"Query intent: {query_intent}")
            print(f"Query categories: {query_categories}")
            print(f"Top result context: {scored_results[0][0].metadata.get('document_source_type', 'unknown')}")
            print(f"Top result authority: {scored_results[0][0].metadata.get('authority_score', 0.5):.2f}")
        
        # Return top k documents
        return [doc for doc, score in scored_results[:k]]

def create_ramit_enhanced_retriever(vector_store, search_kwargs: Optional[Dict[str, Any]] = None):
    """
    Create a Ramit-enhanced retriever that prioritizes content with high Ramit-specific scores
    
    Args:
        vector_store: The underlying vector store
        search_kwargs: Additional search parameters
        
    Returns:
        RamitEnhancedRetriever instance
    """
    if search_kwargs is None:
        search_kwargs = {"k": 5}
    
    return RamitEnhancedRetriever(vector_store, **search_kwargs)