import os
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_pdfs_from_directory(directory_path: str, classify_documents: bool = True) -> List[Dict[str, Any]]:
    """
    Recursively loads all PDF files from a directory and its subdirectories.
    
    Args:
        directory_path: Path to the directory containing PDF files
        classify_documents: Whether to classify documents for context-aware processing
        
    Returns:
        List of document chunks with metadata
    """
    documents = []
    
    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.pdf') and not file.startswith('._'):
                try:
                    file_path = os.path.join(root, file)
                    
                    # Extract module information from path
                    relative_path = os.path.relpath(file_path, directory_path)
                    parts = relative_path.split(os.sep)
                    module = parts[0] if parts else "Unknown"
                    
                    # Load PDF
                    loader = PyPDFLoader(file_path)
                    pdf_documents = loader.load()
                    
                    # Add metadata
                    for doc in pdf_documents:
                        doc.metadata["source"] = file_path
                        doc.metadata["module"] = module
                        doc.metadata["filename"] = file
                    
                    documents.extend(pdf_documents)
                    print(f"Loaded: {file_path}")
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    
    # Classify documents if requested
    if classify_documents and documents:
        print("Classifying documents for context-aware processing...")
        try:
            from .configurable_document_classifier import classify_documents, add_document_classification_metadata
            
            # Classify all documents
            classifications = classify_documents(documents)
            
            # Add classification metadata to each document
            for doc, classification in zip(documents, classifications):
                add_document_classification_metadata(doc, classification)
            
            print(f"Classified {len(documents)} documents with context metadata")
            
            # Log classification summary
            source_types = {}
            teaching_contexts = {}
            avg_authority = 0
            
            for classification in classifications:
                source_type = classification.document_source_type.value
                teaching_context = classification.teaching_context.value
                
                source_types[source_type] = source_types.get(source_type, 0) + 1
                teaching_contexts[teaching_context] = teaching_contexts.get(teaching_context, 0) + 1
                avg_authority += classification.authority_score
            
            avg_authority /= len(classifications)
            
            print(f"Document Source Types: {source_types}")
            print(f"Teaching Contexts: {teaching_contexts}")
            print(f"Average Authority Score: {avg_authority:.2f}")
            
        except ImportError as e:
            print(f"Warning: Could not import document classifier: {e}")
        except Exception as e:
            print(f"Warning: Error during document classification: {e}")
    
    return documents

def split_documents(documents: List[Dict[str, Any]], 
                   chunk_size: int = 1000, 
                   chunk_overlap: int = 100, 
                   enhance_with_expert_analysis: bool = True,
                   use_semantic_chunking: bool = True,
                   expert_config_path: str = None) -> List[Dict[str, Any]]:
    """
    Splits documents into smaller chunks for better processing and optionally enhances
    with expert-specific semantic analysis.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk (for traditional chunking)
        chunk_overlap: Overlap between chunks
        enhance_with_expert_analysis: Whether to add expert-specific metadata
        use_semantic_chunking: Whether to use semantic-aware chunking
        expert_config_path: Path to expert configuration file
        
    Returns:
        List of document chunks with enhanced metadata
    """
    
    if use_semantic_chunking:
        print("Using semantic-aware chunking to preserve framework coherence...")
        try:
            from .semantic_chunker import semantic_split_documents
            chunks = semantic_split_documents(
                documents, 
                macro_chunk_tokens=chunk_size * 2,  # Larger macro chunks in tokens
                micro_chunk_tokens=chunk_size,     # Micro chunks in tokens
                overlap_tokens=chunk_overlap       # Overlap in tokens
            )
            print(f"Semantic chunking: {len(documents)} documents → {len(chunks)} semantic chunks")
        except ImportError as e:
            print(f"Warning: Could not import semantic chunker: {e}")
            print("Falling back to traditional chunking...")
            use_semantic_chunking = False
        except Exception as e:
            print(f"Warning: Error during semantic chunking: {e}")
            print("Falling back to traditional chunking...")
            use_semantic_chunking = False
    
    if not use_semantic_chunking:
        # Fall back to traditional chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Traditional chunking: {len(documents)} documents → {len(chunks)} chunks")
    
    if enhance_with_expert_analysis:
        print("Enhancing chunks with expert-specific semantic analysis...")
        try:
            from .expert_analyzer import enhance_document_metadata
            chunks = enhance_document_metadata(chunks, expert_config_path)
            print(f"Enhanced {len(chunks)} chunks with expert-specific metadata")
        except ImportError as e:
            print(f"Warning: Could not import expert analyzer: {e}")
        except Exception as e:
            print(f"Warning: Error during expert analysis: {e}")
    
    return chunks 