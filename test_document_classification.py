#!/usr/bin/env python3
"""
Test script for document classification system

This script validates the document classification accuracy and tests
context-aware retrieval improvements.
"""

import os
import sys
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.document_classifier import DocumentClassifier, DocumentSourceType, TeachingContext, ConfidenceLevel
from src.utils.pdf_loader import load_pdfs_from_directory
from src.utils.vector_store import create_vector_store
from src.utils.ramit_retriever import create_ramit_enhanced_retriever
from langchain.schema.document import Document

def create_test_documents() -> List[Document]:
    """Create test documents with known characteristics for validation"""
    test_documents = [
        # Structured lesson example
        Document(
            page_content="""
            The Customer Research Framework
            
            Here's the exact system I use for customer research. This proven framework 
            has been tested with thousands of students and consistently delivers results.
            
            Step 1: Identify your target customer
            Step 2: Conduct in-depth interviews
            Step 3: Analyze patterns and insights
            Step 4: Create customer personas
            
            This systematic approach ensures you understand your customers deeply.
            """,
            metadata={"filename": "customer_research_framework.pdf", "source": "test"}
        ),
        
        # Live Q&A example
        Document(
            page_content="""
            Ramit: That's a great question from Sarah in the chat. She's asking about 
            pricing for her consulting services. 
            
            Student: How do I know if I'm charging enough?
            
            Ramit: It depends on your situation. In your case, I'd recommend starting 
            with market research. What I would do is look at what others in your space 
            are charging and position yourself accordingly. My recommendation would be 
            to test different price points.
            """,
            metadata={"filename": "live_qa_session_pricing.pdf", "source": "test"}
        ),
        
        # Student teardown example
        Document(
            page_content="""
            Student Teardown: How Maria Made $50K in 6 Months
            
            Let me tell you about Maria, one of our students who transformed her 
            freelance business. This is a real example of what's possible when you 
            apply the frameworks correctly.
            
            Before: Maria was struggling to find clients and charging $25/hour
            After: She landed three high-paying clients at $150/hour
            
            Here's exactly what she did and the results she achieved...
            """,
            metadata={"filename": "student_teardown_maria.pdf", "source": "test"}
        ),
        
        # Behind the scenes example
        Document(
            page_content="""
            Behind the Scenes: The Truth About Scaling Your Business
            
            This is exclusive content I rarely discuss publicly. What we don't talk 
            about enough is the psychological challenge of scaling. The real story 
            behind successful entrepreneurs is different from what you see online.
            
            Here's what I've learned from working with thousands of students...
            """,
            metadata={"filename": "behind_scenes_scaling.pdf", "source": "test"}
        ),
        
        # Business makeover example
        Document(
            page_content="""
            Business Makeover: What's Wrong with Your Pricing Strategy
            
            Let's diagnose the problems with your current pricing. The root cause 
            of most pricing issues is a fundamental misunderstanding of value.
            
            Analysis shows that 90% of people underprice their services. The 
            symptoms of underpricing include: working too many hours, attracting 
            low-quality clients, and feeling undervalued.
            """,
            metadata={"filename": "business_makeover_pricing.pdf", "source": "test"}
        )
    ]
    
    return test_documents

def test_document_classification():
    """Test document classification accuracy"""
    print("Testing Document Classification System")
    print("=" * 50)
    
    # Initialize classifier
    classifier = DocumentClassifier()
    
    # Create test documents
    test_documents = create_test_documents()
    
    # Expected classifications (ground truth)
    expected_classifications = [
        (DocumentSourceType.STRUCTURED_LESSON, TeachingContext.SYSTEMATIC_INSTRUCTION, ConfidenceLevel.DEFINITIVE_FRAMEWORK),
        (DocumentSourceType.LIVE_QA, TeachingContext.SITUATIONAL_ADVICE, ConfidenceLevel.SUGGESTED_APPROACH),
        (DocumentSourceType.STUDENT_TEARDOWN, TeachingContext.EXAMPLE_APPLICATION, ConfidenceLevel.DEFINITIVE_FRAMEWORK),
        (DocumentSourceType.BEHIND_SCENES, TeachingContext.SYSTEMATIC_INSTRUCTION, ConfidenceLevel.EXPLORATORY),
        (DocumentSourceType.BUSINESS_MAKEOVER, TeachingContext.DIAGNOSTIC, ConfidenceLevel.SUGGESTED_APPROACH)
    ]
    
    # Test each document
    results = []
    for i, (doc, expected) in enumerate(zip(test_documents, expected_classifications)):
        print(f"\nTest {i+1}: {doc.metadata['filename']}")
        print("-" * 30)
        
        # Classify document
        classification = classifier.classify_document(doc)
        
        # Check results
        source_correct = classification.document_source_type == expected[0]
        context_correct = classification.teaching_context == expected[1]
        confidence_correct = classification.confidence_level == expected[2]
        
        print(f"Document Source Type: {classification.document_source_type.value} {'✓' if source_correct else '✗'}")
        print(f"Teaching Context: {classification.teaching_context.value} {'✓' if context_correct else '✗'}")
        print(f"Confidence Level: {classification.confidence_level.value} {'✓' if confidence_correct else '✗'}")
        print(f"Authority Score: {classification.authority_score:.2f}")
        print(f"Classification Confidence: {classification.classification_confidence:.2f}")
        
        # Show quality indicators
        quality = classification.content_quality_indicators
        print(f"Quality Indicators:")
        print(f"  Framework Density: {quality.get('framework_density', 0):.2f}")
        print(f"  Tactical Density: {quality.get('tactical_density', 0):.2f}")
        print(f"  Case Study Density: {quality.get('case_study_density', 0):.2f}")
        print(f"  Contrarian Density: {quality.get('contrarian_density', 0):.2f}")
        
        results.append({
            'document': doc.metadata['filename'],
            'source_correct': source_correct,
            'context_correct': context_correct,
            'confidence_correct': confidence_correct,
            'authority_score': classification.authority_score,
            'classification_confidence': classification.classification_confidence
        })
    
    # Calculate overall accuracy
    total_tests = len(results) * 3  # 3 aspects per document
    correct_predictions = sum(
        r['source_correct'] + r['context_correct'] + r['confidence_correct']
        for r in results
    )
    
    accuracy = correct_predictions / total_tests
    print(f"\nOverall Classification Accuracy: {accuracy:.2f} ({correct_predictions}/{total_tests})")
    
    return results

def test_context_aware_retrieval():
    """Test context-aware retrieval improvements"""
    print("\n\nTesting Context-Aware Retrieval")
    print("=" * 50)
    
    # Create test documents with classifications
    test_documents = create_test_documents()
    
    # Add document classifications
    from src.utils.document_classifier import classify_documents, add_document_classification_metadata
    
    classifications = classify_documents(test_documents)
    for doc, classification in zip(test_documents, classifications):
        add_document_classification_metadata(doc, classification)
    
    # Create a simple in-memory vector store for testing
    try:
        vector_store = create_vector_store(test_documents)
        retriever = create_ramit_enhanced_retriever(vector_store)
        
        # Test queries with different intents
        test_queries = [
            ("What is the customer research framework?", "foundational", "structured_lesson"),
            ("I'm struggling with pricing my services", "specific_problems", "live_qa"),
            ("Show me a real example of business success", "examples", "student_teardown"),
            ("What's the systematic approach to scaling?", "systematic", "structured_lesson"),
            ("I need help diagnosing my business problems", "specific_problems", "business_makeover")
        ]
        
        for query, expected_intent, expected_source_type in test_queries:
            print(f"\nQuery: '{query}'")
            print(f"Expected Intent: {expected_intent}")
            print(f"Expected Source Type: {expected_source_type}")
            print("-" * 30)
            
            # Get retrieval results
            results = retriever.get_relevant_documents(query)
            
            if results:
                top_result = results[0]
                actual_source_type = top_result.metadata.get('document_source_type', 'unknown')
                authority_score = top_result.metadata.get('authority_score', 0.5)
                
                print(f"Top Result: {top_result.metadata.get('filename', 'unknown')}")
                print(f"Actual Source Type: {actual_source_type}")
                print(f"Authority Score: {authority_score:.2f}")
                print(f"Match: {'✓' if actual_source_type == expected_source_type else '✗'}")
            else:
                print("No results found")
    
    except Exception as e:
        print(f"Error in context-aware retrieval test: {e}")
        print("This may be due to missing dependencies or vector store setup")

def test_query_intent_classification():
    """Test query intent classification accuracy"""
    print("\n\nTesting Query Intent Classification")
    print("=" * 50)
    
    from src.utils.ramit_retriever import RamitEnhancedRetriever
    
    # Create a dummy retriever for testing
    retriever = RamitEnhancedRetriever(vector_store=None)
    
    # Test queries with expected intents
    test_queries = [
        ("How do I start a business?", "foundational"),
        ("What is the framework for customer research?", "foundational"),
        ("I'm struggling with pricing", "specific_problems"),
        ("My business is not working", "specific_problems"),
        ("Show me an example of success", "examples"),
        ("Give me a case study", "examples"),
        ("What's the systematic approach?", "systematic"),
        ("I need a step-by-step process", "systematic")
    ]
    
    correct_classifications = 0
    
    for query, expected_intent in test_queries:
        actual_intent = retriever._classify_query_intent(query)
        is_correct = actual_intent == expected_intent
        
        print(f"Query: '{query}'")
        print(f"Expected: {expected_intent}, Actual: {actual_intent} {'✓' if is_correct else '✗'}")
        
        if is_correct:
            correct_classifications += 1
    
    accuracy = correct_classifications / len(test_queries)
    print(f"\nQuery Intent Classification Accuracy: {accuracy:.2f} ({correct_classifications}/{len(test_queries)})")

def main():
    """Run all tests"""
    load_dotenv()
    
    print("Document Classification System Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Document Classification
        classification_results = test_document_classification()
        
        # Test 2: Query Intent Classification
        test_query_intent_classification()
        
        # Test 3: Context-Aware Retrieval (if vector store is available)
        test_context_aware_retrieval()
        
        print("\n\nTest Suite Complete!")
        print("=" * 60)
        
        # Summary
        if classification_results:
            avg_authority = sum(r['authority_score'] for r in classification_results) / len(classification_results)
            avg_confidence = sum(r['classification_confidence'] for r in classification_results) / len(classification_results)
            
            print(f"Average Authority Score: {avg_authority:.2f}")
            print(f"Average Classification Confidence: {avg_confidence:.2f}")
        
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()