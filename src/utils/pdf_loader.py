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

def split_documents(documents: List[Dict[str, Any]], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Splits documents into smaller chunks for better processing.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks")
    
    return chunks 