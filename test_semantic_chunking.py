#!/usr/bin/env python3
"""
Test script for semantic chunking validation.
This script tests framework preservation and chunk coherence.
"""

import os
import sys
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.pdf_loader import load_pdfs_from_directory, split_documents
from src.utils.semantic_chunker import semantic_split_documents

def analyze_chunk_quality(chunks: List[Any], chunking_type: str) -> Dict[str, float]:
    """Analyze the quality of chunks"""
    if not chunks:
        return {}
    
    total_chunks = len(chunks)
    
    # Basic metrics
    avg_length = sum(len(chunk.page_content) for chunk in chunks) / total_chunks
    
    # Count chunks with semantic metadata
    semantic_chunks = sum(1 for chunk in chunks 
                         if chunk.metadata.get("semantic_quality_score") is not None)
    
    # Framework coherence analysis
    framework_chunks = sum(1 for chunk in chunks 
                          if any(term in chunk.page_content.lower() 
                               for term in ["framework", "process", "step", "system"]))
    
    # Case study analysis
    case_study_chunks = sum(1 for chunk in chunks 
                           if any(term in chunk.page_content.lower() 
                                for term in ["student", "example", "case study", "story"]))
    
    # Tactical sequence analysis  
    tactical_chunks = sum(1 for chunk in chunks 
                         if any(term in chunk.page_content.lower() 
                              for term in ["step 1", "step 2", "first", "second", "then"]))
    
    # Calculate quality scores if available
    quality_scores = []
    completeness_scores = []
    coherence_scores = []
    
    for chunk in chunks:
        quality = chunk.metadata.get("semantic_quality_score")
        if quality is not None:
            quality_scores.append(float(quality))
        
        completeness = chunk.metadata.get("conceptual_completeness")
        if completeness is not None:
            completeness_scores.append(float(completeness))
            
        coherence = chunk.metadata.get("framework_coherence")
        if coherence is not None:
            coherence_scores.append(float(coherence))
    
    return {
        "chunking_type": chunking_type,
        "total_chunks": total_chunks,
        "average_length": avg_length,
        "semantic_chunks": semantic_chunks,
        "framework_chunks": framework_chunks,
        "case_study_chunks": case_study_chunks,
        "tactical_chunks": tactical_chunks,
        "avg_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
        "avg_completeness": sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0,
        "avg_coherence": sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0,
        "framework_preservation": framework_chunks / total_chunks if total_chunks > 0 else 0,
        "case_study_preservation": case_study_chunks / total_chunks if total_chunks > 0 else 0,
        "tactical_preservation": tactical_chunks / total_chunks if total_chunks > 0 else 0
    }

def examine_framework_preservation(chunks: List[Any], framework_name: str) -> Dict[str, Any]:
    """Examine how well a specific framework is preserved across chunks"""
    framework_chunks = []
    
    for i, chunk in enumerate(chunks):
        content = chunk.page_content.lower()
        if framework_name.lower() in content:
            framework_chunks.append({
                "chunk_index": i,
                "content_length": len(chunk.page_content),
                "content_preview": chunk.page_content[:200] + "...",
                "chunk_type": chunk.metadata.get("chunk_type", "unknown"),
                "quality_score": chunk.metadata.get("semantic_quality_score", 0),
                "framework_coherence": chunk.metadata.get("framework_coherence", 0),
                "boundary_type": chunk.metadata.get("boundary_type", "none")
            })
    
    return {
        "framework": framework_name,
        "total_occurrences": len(framework_chunks),
        "chunks": framework_chunks
    }

def test_semantic_chunking():
    """Test semantic chunking vs traditional chunking"""
    
    print("="*80)
    print("SEMANTIC CHUNKING VALIDATION TEST")
    print("="*80)
    
    # Test with customer research content
    test_dir = "./01 playbooks/05 Map Your Road to Profit"
    if not os.path.exists(test_dir):
        print(f"Test directory not found: {test_dir}")
        return
    
    print(f"\\nLoading documents from: {test_dir}")
    documents = load_pdfs_from_directory(test_dir)
    
    if not documents:
        print("No documents found!")
        return
    
    print(f"Loaded {len(documents)} documents")
    
    # Test both chunking approaches
    print("\\n" + "="*60)
    print("TRADITIONAL CHUNKING TEST")
    print("="*60)
    
    traditional_chunks = split_documents(
        documents[:3],  # Test with first 3 documents
        chunk_size=800,
        chunk_overlap=100,
        enhance_with_ramit_analysis=True,
        use_semantic_chunking=False
    )
    
    trad_analysis = analyze_chunk_quality(traditional_chunks, "Traditional")
    
    print("\\n" + "="*60)
    print("SEMANTIC CHUNKING TEST") 
    print("="*60)
    
    semantic_chunks = split_documents(
        documents[:3],  # Test with same documents
        chunk_size=800,
        chunk_overlap=100,
        enhance_with_ramit_analysis=True,
        use_semantic_chunking=True
    )
    
    semantic_analysis = analyze_chunk_quality(semantic_chunks, "Semantic")
    
    # Compare results
    print("\\n" + "="*60)
    print("CHUNKING COMPARISON")
    print("="*60)
    
    metrics = [
        ("Total Chunks", "total_chunks"),
        ("Average Length", "average_length"),
        ("Framework Chunks %", "framework_preservation"),
        ("Case Study Chunks %", "case_study_preservation"),
        ("Tactical Chunks %", "tactical_preservation"),
        ("Avg Quality Score", "avg_quality_score"),
        ("Avg Completeness", "avg_completeness"),
        ("Avg Coherence", "avg_coherence")
    ]
    
    print(f"{'Metric':<25} {'Traditional':<15} {'Semantic':<15} {'Improvement':<15}")
    print("-" * 70)
    
    for metric_name, metric_key in metrics:
        trad_val = trad_analysis.get(metric_key, 0)
        sem_val = semantic_analysis.get(metric_key, 0)
        
        if metric_key in ["framework_preservation", "case_study_preservation", "tactical_preservation"]:
            improvement = f"{((sem_val - trad_val) * 100):+.1f}%"
            trad_display = f"{trad_val * 100:.1f}%"
            sem_display = f"{sem_val * 100:.1f}%"
        elif metric_key == "average_length":
            improvement = f"{sem_val - trad_val:+.0f}"
            trad_display = f"{trad_val:.0f}"
            sem_display = f"{sem_val:.0f}"
        else:
            improvement = f"{sem_val - trad_val:+.2f}"
            trad_display = f"{trad_val:.2f}"
            sem_display = f"{sem_val:.2f}"
        
        print(f"{metric_name:<25} {trad_display:<15} {sem_display:<15} {improvement:<15}")
    
    # Specific framework analysis
    print("\\n" + "="*60)
    print("FRAMEWORK PRESERVATION ANALYSIS")
    print("="*60)
    
    frameworks_to_test = ["customer research", "profit playbook", "framework"]
    
    for framework in frameworks_to_test:
        print(f"\\n--- {framework.upper()} PRESERVATION ---")
        
        trad_framework = examine_framework_preservation(traditional_chunks, framework)
        sem_framework = examine_framework_preservation(semantic_chunks, framework)
        
        print(f"Traditional: {trad_framework['total_occurrences']} chunks contain '{framework}'")
        print(f"Semantic: {sem_framework['total_occurrences']} chunks contain '{framework}'")
        
        if sem_framework['chunks']:
            print("\\nSemantic chunks with framework:")
            for chunk_info in sem_framework['chunks'][:3]:  # Show first 3
                print(f"  Chunk {chunk_info['chunk_index']}: {chunk_info['chunk_type']} "
                      f"(Quality: {chunk_info['quality_score']:.2f}, "
                      f"Coherence: {chunk_info['framework_coherence']:.2f})")
                print(f"    {chunk_info['content_preview']}")
    
    # Show sample chunks for quality comparison
    print("\\n" + "="*60)
    print("CHUNK QUALITY SAMPLES")
    print("="*60)
    
    print("\\n--- HIGH-QUALITY SEMANTIC CHUNKS ---")
    high_quality_chunks = [chunk for chunk in semantic_chunks 
                          if chunk.metadata.get("semantic_quality_score", 0) > 0.7]
    
    for i, chunk in enumerate(high_quality_chunks[:2]):
        print(f"\\nChunk {i+1}: {chunk.metadata.get('chunk_type', 'unknown')} "
              f"(Quality: {chunk.metadata.get('semantic_quality_score', 0):.2f})")
        print(f"Length: {len(chunk.page_content)} characters")
        print(f"Content: {chunk.page_content[:300]}...")
    
    print("\\nTest completed! Semantic chunking should show improved framework preservation.")

if __name__ == "__main__":
    test_semantic_chunking()