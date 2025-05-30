import os
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

def load_resume(file_path: str) -> List[Document]:
    """
    Loads a resume file (PDF or text) and adds appropriate metadata.
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        List of document chunks with resume-specific metadata
    """
    documents = []
    
    try:
        # Determine loader based on file extension
        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.lower().endswith('.txt'):
            loader = TextLoader(file_path)
        elif file_path.lower().endswith(('.md', '.docx')):
            # Use UnstructuredFileLoader for more complex files
            loader = UnstructuredFileLoader(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Load document
        resume_documents = loader.load()
        
        # Add metadata
        for doc in resume_documents:
            doc.metadata["source"] = file_path
            doc.metadata["filename"] = os.path.basename(file_path)
            doc.metadata["document_type"] = "resume"
            doc.metadata["content_type"] = "personal_information"
            
        documents.extend(resume_documents)
        print(f"Loaded resume: {file_path}")
        
    except Exception as e:
        print(f"Error loading resume {file_path}: {e}")
    
    return documents

def process_resume(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    """
    Loads and processes a resume file, splitting it into chunks with metadata.
    
    Args:
        file_path: Path to the resume file
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of processed document chunks
    """
    # Load the resume
    documents = load_resume(file_path)
    
    if not documents:
        print("No resume document loaded. Please check the file path.")
        return []
    
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Ensure all chunks have the resume metadata
    for chunk in chunks:
        # Make sure each chunk is properly tagged as resume information
        chunk.metadata["document_type"] = "resume"
        chunk.metadata["content_type"] = "personal_information"
    
    print(f"Split resume document into {len(chunks)} chunks")
    
    return chunks 