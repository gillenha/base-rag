"""
Configurable Enhanced Retriever

Custom retriever that uses expert-specific metadata and document classification
to improve semantic matching and prioritize content that matches the expert's 
distinctive methodology and teaching context. Configurable for any expert.
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from pydantic import Field
import re
from .expert_analyzer import load_expert_config

class ConfigurableEnhancedRetriever(BaseRetriever):
    """
    Enhanced retriever that uses expert-specific metadata and document classification
    to improve search results by prioritizing content that matches the expert's frameworks,
    approaches, and teaching context.
    """
    
    vector_store: Any = Field()
    expert_keywords: Dict[str, List[str]] = Field(default_factory=dict)
    query_type_priorities: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    expert_name: str = Field(default="expert")
    
    def __init__(self, vector_store, config_path: Optional[str] = None, **kwargs):
        # Load expert configuration
        config = load_expert_config(config_path)
        expert_name = config.get('expert_profile', {}).get('name', 'Expert').lower().replace(' ', '_')
        
        super().__init__(
            vector_store=vector_store, 
            expert_keywords=self._initialize_expert_keywords(config),
            query_type_priorities=self._initialize_query_type_priorities(config),
            expert_name=expert_name,
            **kwargs
        )
        
    def _initialize_expert_keywords(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Initialize keyword mappings for different types of queries from config"""
        keywords = {}
        
        # Extract keywords from query intent classification
        intent_config = config.get('query_intent_classification', {})
        for intent, intent_data in intent_config.items():
            if isinstance(intent_data, dict):
                intent_keywords = intent_data.get('keywords', [])
                keywords[intent] = intent_keywords
            elif isinstance(intent_data, list):
                keywords[intent] = intent_data
        
        # Add framework keywords
        frameworks = config.get('frameworks', {})
        for framework_name, framework_data in frameworks.items():
            if isinstance(framework_data, dict):
                framework_keywords = framework_data.get('keywords', [])
                keywords[f"framework_{framework_name}"] = framework_keywords
        
        return keywords
    
    def _classify_query(self, query: str) -> List[str]:
        """Classify the query to understand what type of expert content to prioritize"""
        query_lower = query.lower()
        matching_categories = []
        
        for category, keywords in self.expert_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                matching_categories.append(category)
        
        return matching_categories
    
    def _initialize_query_type_priorities(self, config: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Initialize priority weights for different query types and document contexts from config"""
        priorities = config.get('retrieval_priorities', {})
        
        # Add default priorities if not specified
        if not priorities:
            priorities = {
                "foundational": {
                    "structured_lesson": 1.0,
                    "systematic_instruction": 1.0,
                    "high_authority": 1.0,
                    "live_qa": 0.4,
                    "situational_advice": 0.3,
                    "low_authority": 0.2
                },
                "specific_problems": {
                    "live_qa": 1.0,
                    "situational_advice": 1.0,
                    "troubleshooting": 1.0,
                    "structured_lesson": 0.6,
                    "systematic_instruction": 0.5,
                    "high_authority": 0.7
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
                    "high_authority": 1.0,
                    "medium_authority": 0.8,
                    "live_qa": 0.3,
                    "low_authority": 0.2
                }
            }
            
        return priorities
    
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
    
    def _calculate_expert_relevance_score(self, doc: Document, query_categories: List[str], query_intent: str) -> float:
        """Calculate relevance score based on expert-specific metadata and document classification"""
        metadata = doc.metadata
        score = 0.0
        
        # Base score from expert content types (support both new and legacy naming)
        primary_type = metadata.get(f"{self.expert_name}_primary_type") or metadata.get("ramit_primary_type", "general")
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
            expert_frameworks = metadata.get(f"{self.expert_name}_frameworks", "") or metadata.get("ramit_frameworks", "")
            
            if "first_sale" in category and "authentic_selling" in expert_frameworks:
                score += 0.5
            elif "customer_research" in category and "customer_research" in expert_frameworks:
                score += 0.5
            elif "offers" in category and "winning_offer" in expert_frameworks:
                score += 0.5
            elif "contrarian" in category:
                score += contrarian_density * 0.5
            elif "frameworks" in category:
                score += framework_density * 0.5
            elif "testing" in category and tactical_density > 0.3:
                score += tactical_density * 0.3
        
        # Boost for high expert scores (support both new and legacy naming)
        contrarian_score = metadata.get(f"{self.expert_name}_contrarian_score", 0) or metadata.get("ramit_contrarian_score", 0)
        tactical_score = metadata.get(f"{self.expert_name}_tactical_score", 0) or metadata.get("ramit_tactical_score", 0)
        framework_score = metadata.get(f"{self.expert_name}_framework_score", 0) or metadata.get("ramit_framework_score", 0)
        case_study_score = metadata.get(f"{self.expert_name}_case_study_score", 0) or metadata.get("ramit_case_study_score", 0)
        
        score += contrarian_score * 0.15
        score += tactical_score * 0.15
        score += framework_score * 0.15
        score += case_study_score * 0.1
        
        # Boost for specific expert signatures
        expert_signatures = metadata.get(f"{self.expert_name}_signatures", "") or metadata.get("ramit_signatures", "")
        signatures_list = expert_signatures.split(",") if expert_signatures else []
        signature_boost = len([s for s in signatures_list if s.strip()]) * 0.1
        score += min(signature_boost, 0.3)  # Cap at 0.3
        
        return score
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """Retrieve documents with context-aware expert-enhanced scoring"""
        
        # Get initial results from vector search (default k=5, get more to rerank)
        k = 5
        initial_results = self.vector_store.similarity_search(query, k=k*2)  # Get more to rerank
        
        # Classify the query
        query_categories = self._classify_query(query)
        query_intent = self._classify_query_intent(query)
        
        # Calculate expert relevance scores and rerank
        scored_results = []
        for doc in initial_results:
            expert_score = self._calculate_expert_relevance_score(doc, query_categories, query_intent)
            scored_results.append((doc, expert_score))
        
        # Sort by expert relevance score (descending)
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Debug logging for context-aware retrieval
        if scored_results:
            print(f"Query intent: {query_intent}")
            print(f"Query categories: {query_categories}")
            print(f"Top result context: {scored_results[0][0].metadata.get('document_source_type', 'unknown')}")
            print(f"Top result authority: {scored_results[0][0].metadata.get('authority_score', 0.5):.2f}")
        
        # Return top k documents
        return [doc for doc, score in scored_results[:k]]

def create_expert_enhanced_retriever(vector_store, config_path: Optional[str] = None, search_kwargs: Optional[Dict[str, Any]] = None):
    """
    Create an expert-enhanced retriever that prioritizes content with high expert-specific scores
    
    Args:
        vector_store: The underlying vector store
        config_path: Path to expert configuration file
        search_kwargs: Additional search parameters
        
    Returns:
        ConfigurableEnhancedRetriever instance
    """
    if search_kwargs is None:
        search_kwargs = {"k": 5}
    
    return ConfigurableEnhancedRetriever(vector_store, config_path, **search_kwargs)