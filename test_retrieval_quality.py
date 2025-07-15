#!/usr/bin/env python3
"""
Test script for retrieval quality improvements

This script tests the enhanced RAG system with document classification
and context-aware retrieval against different query types.
"""

import os
import sys
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_retrieval_with_real_data():
    """Test retrieval quality with actual course content if available"""
    print("Testing Retrieval Quality with Real Data")
    print("=" * 50)
    
    try:
        from src.utils.pdf_loader import load_pdfs_from_directory
        from src.utils.vector_store import create_vector_store
        from src.utils.ramit_retriever import create_ramit_enhanced_retriever
        
        # Check if course content directory exists
        course_content_dir = os.getenv("COURSE_CONTENT_DIR", "./01 playbooks")
        
        if not os.path.exists(course_content_dir):
            print(f"Course content directory not found: {course_content_dir}")
            print("Please set COURSE_CONTENT_DIR environment variable or ensure course content is available")
            return
        
        # Load documents with classification
        print("Loading documents with classification...")
        documents = load_pdfs_from_directory(course_content_dir, classify_documents=True)
        
        if not documents:
            print("No documents found in course content directory")
            return
        
        print(f"Loaded {len(documents)} documents")
        
        # Create vector store
        print("Creating vector store...")
        vector_store = create_vector_store(documents)
        
        # Create enhanced retriever
        retriever = create_ramit_enhanced_retriever(vector_store)
        
        # Test queries designed to benefit from context-aware retrieval
        test_queries = [
            {
                "query": "How do I get people interested in my business?",
                "expected_context": "structured_lesson",
                "description": "Foundational question should prioritize systematic frameworks"
            },
            {
                "query": "I'm struggling to close sales, what should I do?",
                "expected_context": "live_qa",
                "description": "Problem-solving question should prioritize situational advice"
            },
            {
                "query": "Show me a real example of someone who succeeded with customer research",
                "expected_context": "student_teardown",
                "description": "Example request should prioritize case studies and teardowns"
            },
            {
                "query": "What's wrong with my pricing strategy?",
                "expected_context": "business_makeover",
                "description": "Diagnostic question should prioritize troubleshooting content"
            },
            {
                "query": "Give me the exact framework for winning offers",
                "expected_context": "structured_lesson",
                "description": "Systematic request should prioritize definitive frameworks"
            }
        ]
        
        print("\nTesting Context-Aware Retrieval:")
        print("-" * 40)
        
        for i, test_case in enumerate(test_queries):
            print(f"\nTest {i+1}: {test_case['description']}")
            print(f"Query: '{test_case['query']}'")
            print(f"Expected Context: {test_case['expected_context']}")
            
            # Get retrieval results
            results = retriever.get_relevant_documents(test_case['query'])
            
            if results:
                top_result = results[0]
                metadata = top_result.metadata
                
                # Extract classification metadata
                source_type = metadata.get('document_source_type', 'unknown')
                teaching_context = metadata.get('teaching_context', 'unknown')
                authority_score = metadata.get('authority_score', 0.5)
                confidence_level = metadata.get('confidence_level', 'unknown')
                
                print(f"Top Result Source: {metadata.get('filename', 'unknown')}")
                print(f"Document Source Type: {source_type}")
                print(f"Teaching Context: {teaching_context}")
                print(f"Authority Score: {authority_score:.2f}")
                print(f"Confidence Level: {confidence_level}")
                
                # Check if context matches expectation
                context_match = (source_type == test_case['expected_context'] or 
                               teaching_context == test_case['expected_context'])
                print(f"Context Match: {'✓' if context_match else '✗'}")
                
                # Show content preview
                content_preview = top_result.page_content[:200] + "..." if len(top_result.page_content) > 200 else top_result.page_content
                print(f"Content Preview: {content_preview}")
            else:
                print("No results found")
        
        # Test authority scoring
        print("\n\nTesting Authority Scoring:")
        print("-" * 30)
        
        authority_test_queries = [
            "What's the proven framework for customer research?",
            "I think pricing might be important",
            "Here's my opinion on business strategy"
        ]
        
        for query in authority_test_queries:
            print(f"\nQuery: '{query}'")
            results = retriever.get_relevant_documents(query)
            
            if results:
                for j, result in enumerate(results[:3]):  # Show top 3
                    authority = result.metadata.get('authority_score', 0.5)
                    source_type = result.metadata.get('document_source_type', 'unknown')
                    filename = result.metadata.get('filename', 'unknown')
                    
                    print(f"  {j+1}. {filename} (Authority: {authority:.2f}, Type: {source_type})")
        
    except Exception as e:
        print(f"Error in retrieval testing: {e}")
        import traceback
        traceback.print_exc()

def test_document_type_distribution():
    """Test the distribution of document types in the corpus"""
    print("\n\nTesting Document Type Distribution")
    print("=" * 50)
    
    try:
        from src.utils.pdf_loader import load_pdfs_from_directory
        
        course_content_dir = os.getenv("COURSE_CONTENT_DIR", "./01 playbooks")
        
        if not os.path.exists(course_content_dir):
            print(f"Course content directory not found: {course_content_dir}")
            return
        
        # Load documents with classification
        documents = load_pdfs_from_directory(course_content_dir, classify_documents=True)
        
        if not documents:
            print("No documents found")
            return
        
        # Analyze document type distribution
        source_types = {}
        teaching_contexts = {}
        confidence_levels = {}
        authority_scores = []
        
        for doc in documents:
            metadata = doc.metadata
            
            # Count source types
            source_type = metadata.get('document_source_type', 'unknown')
            source_types[source_type] = source_types.get(source_type, 0) + 1
            
            # Count teaching contexts
            teaching_context = metadata.get('teaching_context', 'unknown')
            teaching_contexts[teaching_context] = teaching_contexts.get(teaching_context, 0) + 1
            
            # Count confidence levels
            confidence_level = metadata.get('confidence_level', 'unknown')
            confidence_levels[confidence_level] = confidence_levels.get(confidence_level, 0) + 1
            
            # Collect authority scores
            authority_score = metadata.get('authority_score', 0.5)
            authority_scores.append(authority_score)
        
        print(f"Total Documents: {len(documents)}")
        print(f"Total Pages: {sum(1 for doc in documents if doc.page_content)}")
        
        print("\nDocument Source Type Distribution:")
        for source_type, count in sorted(source_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(documents)) * 100
            print(f"  {source_type}: {count} ({percentage:.1f}%)")
        
        print("\nTeaching Context Distribution:")
        for context, count in sorted(teaching_contexts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(documents)) * 100
            print(f"  {context}: {count} ({percentage:.1f}%)")
        
        print("\nConfidence Level Distribution:")
        for confidence, count in sorted(confidence_levels.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(documents)) * 100
            print(f"  {confidence}: {count} ({percentage:.1f}%)")
        
        # Authority score statistics
        if authority_scores:
            avg_authority = sum(authority_scores) / len(authority_scores)
            min_authority = min(authority_scores)
            max_authority = max(authority_scores)
            
            print(f"\nAuthority Score Statistics:")
            print(f"  Average: {avg_authority:.2f}")
            print(f"  Min: {min_authority:.2f}")
            print(f"  Max: {max_authority:.2f}")
        
    except Exception as e:
        print(f"Error in document type distribution analysis: {e}")
        import traceback
        traceback.print_exc()

def test_query_performance_comparison():
    """Compare retrieval performance before and after context-aware enhancements"""
    print("\n\nTesting Query Performance Comparison")
    print("=" * 50)
    
    try:
        from src.utils.pdf_loader import load_pdfs_from_directory
        from src.utils.vector_store import create_vector_store
        from src.utils.ramit_retriever import create_ramit_enhanced_retriever
        import time
        
        course_content_dir = os.getenv("COURSE_CONTENT_DIR", "./01 playbooks")
        
        if not os.path.exists(course_content_dir):
            print(f"Course content directory not found: {course_content_dir}")
            return
        
        # Load documents with classification
        documents = load_pdfs_from_directory(course_content_dir, classify_documents=True)
        
        if not documents:
            print("No documents found")
            return
        
        # Create vector store
        vector_store = create_vector_store(documents)
        
        # Create enhanced retriever
        enhanced_retriever = create_ramit_enhanced_retriever(vector_store)
        
        # Test queries
        test_queries = [
            "How do I get people interested in my business?",
            "I'm struggling with pricing",
            "Show me a success story",
            "What's the customer research framework?",
            "Help me diagnose my business problems"
        ]
        
        print(f"Testing {len(test_queries)} queries...")
        
        # Test enhanced retriever
        enhanced_times = []
        enhanced_results = []
        
        for query in test_queries:
            start_time = time.time()
            results = enhanced_retriever.get_relevant_documents(query)
            end_time = time.time()
            
            enhanced_times.append(end_time - start_time)
            enhanced_results.append(results)
        
        # Calculate performance metrics
        avg_time = sum(enhanced_times) / len(enhanced_times)
        total_results = sum(len(results) for results in enhanced_results)
        
        print(f"\nPerformance Metrics:")
        print(f"  Average Query Time: {avg_time:.3f} seconds")
        print(f"  Total Results Retrieved: {total_results}")
        print(f"  Average Results per Query: {total_results / len(test_queries):.1f}")
        
        # Show authority distribution in results
        authority_scores = []
        for results in enhanced_results:
            for result in results:
                authority = result.metadata.get('authority_score', 0.5)
                authority_scores.append(authority)
        
        if authority_scores:
            avg_authority = sum(authority_scores) / len(authority_scores)
            print(f"  Average Authority Score of Results: {avg_authority:.2f}")
        
    except Exception as e:
        print(f"Error in performance comparison: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all retrieval quality tests"""
    load_dotenv()
    
    print("Retrieval Quality Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Document Type Distribution
        test_document_type_distribution()
        
        # Test 2: Context-Aware Retrieval
        test_retrieval_with_real_data()
        
        # Test 3: Performance Comparison
        test_query_performance_comparison()
        
        print("\n\nRetrieval Quality Test Suite Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error running retrieval quality tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()