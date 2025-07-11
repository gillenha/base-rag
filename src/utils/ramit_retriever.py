"""
Ramit-Enhanced Retriever

Custom retriever that uses Ramit-specific metadata to improve semantic matching
and prioritize content that matches Ramit's distinctive methodology.
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from pydantic import Field
import re

class RamitEnhancedRetriever(BaseRetriever):
    """
    Enhanced retriever that uses Ramit-specific metadata to improve search results
    by prioritizing content that matches Ramit's frameworks and approaches.
    """
    
    vector_store: Any = Field()
    ramit_keywords: Dict[str, List[str]] = Field(default_factory=dict)
    
    def __init__(self, vector_store, **kwargs):
        super().__init__(vector_store=vector_store, ramit_keywords=self._initialize_ramit_keywords(), **kwargs)
        
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
    
    def _calculate_ramit_relevance_score(self, doc: Document, query_categories: List[str]) -> float:
        """Calculate relevance score based on Ramit-specific metadata"""
        metadata = doc.metadata
        score = 0.0
        
        # Base score from Ramit content types
        primary_type = metadata.get("ramit_primary_type", "general")
        if primary_type != "general":
            score += 0.3
            
        # Boost for specific query categories
        ramit_frameworks = metadata.get("ramit_frameworks", "").split(",") if metadata.get("ramit_frameworks") else []
        ramit_content_types = metadata.get("ramit_content_types", "").split(",") if metadata.get("ramit_content_types") else []
        
        for category in query_categories:
            if category == "first_sale" and any(f in ramit_frameworks for f in ["authentic_selling"]):
                score += 0.5
            elif category == "customer_research" and "customer_research" in ramit_frameworks:
                score += 0.5
            elif category == "offers" and "winning_offer" in ramit_frameworks:
                score += 0.5
            elif category == "contrarian" and "contrarian" in ramit_content_types:
                score += 0.4
            elif category == "testing" and "testing" in ramit_content_types:
                score += 0.3
            elif category == "frameworks" and metadata.get("ramit_framework_score", 0) > 0.5:
                score += 0.4
        
        # Boost for high Ramit scores
        contrarian_score = metadata.get("ramit_contrarian_score", 0)
        tactical_score = metadata.get("ramit_tactical_score", 0)
        framework_score = metadata.get("ramit_framework_score", 0)
        case_study_score = metadata.get("ramit_case_study_score", 0)
        
        score += contrarian_score * 0.2
        score += tactical_score * 0.15
        score += framework_score * 0.2
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
        """Retrieve documents with Ramit-enhanced scoring"""
        
        # Get initial results from vector search (default k=5, get more to rerank)
        k = 5
        initial_results = self.vector_store.similarity_search(query, k=k*2)  # Get more to rerank
        
        # Classify the query
        query_categories = self._classify_query(query)
        
        # Calculate Ramit relevance scores and rerank
        scored_results = []
        for doc in initial_results:
            ramit_score = self._calculate_ramit_relevance_score(doc, query_categories)
            scored_results.append((doc, ramit_score))
        
        # Sort by Ramit relevance score (descending)
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
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