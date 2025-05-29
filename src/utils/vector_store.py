import os
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema.document import Document

def create_vector_store(documents: List[Document], persist_directory: str = "./chroma_db"):
    """
    Creates a vector store from a list of documents.
    
    Args:
        documents: List of documents to embed and store
        persist_directory: Directory to persist the vector store
        
    Returns:
        A vector store instance
    """
    # Create directory if it doesn't exist
    os.makedirs(persist_directory, exist_ok=True)
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings()
    
    # Create and persist vector store
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    vector_store.persist()
    print(f"Vector store created with {len(documents)} documents and persisted to {persist_directory}")
    
    return vector_store

def load_vector_store(persist_directory: str = "./chroma_db"):
    """
    Loads a vector store from a directory.
    
    Args:
        persist_directory: Directory where the vector store is persisted
        
    Returns:
        A vector store instance
    """
    if not os.path.exists(persist_directory):
        raise FileNotFoundError(f"Vector store directory {persist_directory} does not exist")
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings()
    
    # Load vector store
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    print(f"Loaded vector store from {persist_directory}")
    return vector_store 