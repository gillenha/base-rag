import os
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_pdfs_from_directory(directory_path: str) -> List[Dict[str, Any]]:
    """
    Recursively loads all PDF files from a directory and its subdirectories.
    
    Args:
        directory_path: Path to the directory containing PDF files
        
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
    
    return documents

def split_documents(documents: List[Dict[str, Any]], 
                   chunk_size: int = 1000, 
                   chunk_overlap: int = 100, 
                   enhance_with_ramit_analysis: bool = True,
                   use_semantic_chunking: bool = True) -> List[Dict[str, Any]]:
    """
    Splits documents into smaller chunks for better processing and optionally enhances
    with Ramit-specific semantic analysis.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk (for traditional chunking)
        chunk_overlap: Overlap between chunks
        enhance_with_ramit_analysis: Whether to add Ramit-specific metadata
        use_semantic_chunking: Whether to use semantic-aware chunking
        
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
    
    if enhance_with_ramit_analysis:
        print("Enhancing chunks with Ramit-specific semantic analysis...")
        try:
            from .ramit_analyzer import enhance_document_metadata
            chunks = enhance_document_metadata(chunks)
            print(f"Enhanced {len(chunks)} chunks with Ramit-specific metadata")
        except ImportError as e:
            print(f"Warning: Could not import Ramit analyzer: {e}")
        except Exception as e:
            print(f"Warning: Error during Ramit analysis: {e}")
    
    return chunks 