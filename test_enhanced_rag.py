#!/usr/bin/env python3
"""
Test script for the enhanced RAG system with Ramit-specific metadata.
This script tests the improved semantic retrieval on first sale process questions.
"""

import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.pdf_loader import load_pdfs_from_directory, split_documents
from src.utils.vector_store import create_vector_store, load_vector_store
from src.utils.rag_chain import create_rag_chain, format_response

def test_enhanced_rag():
    """Test the enhanced RAG system with a first sale process question"""
    
    # Load environment variables
    load_dotenv()
    
    print("Testing Enhanced RAG System with Ramit-Specific Metadata")
    print("="*60)
    
    # Test with just the "Get Your First Sale" module for faster testing
    test_dir = "./01 playbooks/04 Get Your First Sale"
    test_vector_store_path = "./test_chroma_db"
    
    print(f"\n1. Loading and processing documents from {test_dir}...")
    documents = load_pdfs_from_directory(test_dir)
    print(f"Loaded {len(documents)} documents")
    
    print("\n2. Splitting documents and enhancing with Ramit analysis...")
    chunks = split_documents(documents, enhance_with_ramit_analysis=True)
    print(f"Created {len(chunks)} enhanced chunks")
    
    # Show some analysis results
    print("\n3. Sample of Ramit-enhanced metadata:")
    ramit_chunks = [c for c in chunks if c.metadata.get("ramit_primary_type", "general") != "general"]
    print(f"Found {len(ramit_chunks)} chunks with Ramit-specific content")
    
    for i, chunk in enumerate(ramit_chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(f"  Primary Type: {chunk.metadata.get('ramit_primary_type')}")
        print(f"  Frameworks: {chunk.metadata.get('ramit_frameworks', [])}")
        print(f"  Signatures: {chunk.metadata.get('ramit_signatures', [])}")
        print(f"  Content: {chunk.page_content[:150]}...")
    
    print(f"\n4. Creating test vector store at {test_vector_store_path}...")
    vector_store = create_vector_store(chunks, test_vector_store_path)
    
    print("\n5. Creating enhanced RAG chain...")
    rag_chain = create_rag_chain(vector_store, "gpt-4")
    
    print("\n6. Testing with first sale process question...")
    test_question = "What is Ramit's process for getting your first sale?"
    
    print(f"Question: {test_question}")
    print("\nGenerating response...")
    
    try:
        response = rag_chain.invoke({"question": test_question})
        formatted_response = format_response(response)
        
        print("\n" + "="*60)
        print("ENHANCED RAG RESPONSE:")
        print("="*60)
        print(formatted_response["answer"])
        
        print("\n" + "="*60)
        print("SOURCES WITH RAMIT METADATA:")
        print("="*60)
        
        for i, source in enumerate(formatted_response["sources"]):
            print(f"\nSource {i+1}:")
            print(f"  Module: {source.get('module', 'Unknown')}")
            print(f"  File: {os.path.basename(source.get('source', 'Unknown'))}")
            
            if "ramit_type" in source:
                print(f"  Ramit Type: {source['ramit_type']}")
                print(f"  Ramit Frameworks: {source.get('ramit_frameworks', [])}")
                print(f"  Ramit Signatures: {source.get('ramit_signatures', [])}")
                scores = source.get('ramit_scores', {})
                print(f"  Scores - Contrarian: {scores.get('contrarian', 0):.2f}, "
                      f"Tactical: {scores.get('tactical', 0):.2f}, "
                      f"Framework: {scores.get('framework', 0):.2f}")
            
            print(f"  Content: {source.get('content', '')}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n7. Cleaning up test vector store...")
    import shutil
    if os.path.exists(test_vector_store_path):
        shutil.rmtree(test_vector_store_path)
        print("Test vector store cleaned up")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_enhanced_rag()