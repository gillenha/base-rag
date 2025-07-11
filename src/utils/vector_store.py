import os
import time
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema.document import Document
from .token_utils import count_tokens, validate_token_limit

def create_vector_store(documents: List[Document], persist_directory: str = "./chroma_db", 
                       batch_size: int = 50, max_tokens_per_batch: int = 200000):
    """
    Creates a vector store from a list of documents with batch processing for token limits.
    
    Args:
        documents: List of documents to embed and store
        persist_directory: Directory to persist the vector store
        batch_size: Maximum number of documents per batch
        max_tokens_per_batch: Maximum tokens per embedding batch
        
    Returns:
        A vector store instance
    """
    # Create directory if it doesn't exist
    os.makedirs(persist_directory, exist_ok=True)
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings()
    
    # Validate document token counts
    validated_documents = []
    for doc in documents:
        token_count = count_tokens(doc.page_content)
        if token_count > 8000:  # OpenAI's per-document limit
            print(f"Warning: Document exceeds 8k tokens ({token_count}), skipping...")
            continue
        validated_documents.append(doc)
    
    if not validated_documents:
        raise ValueError("No valid documents after token validation")
    
    print(f"Processing {len(validated_documents)} validated documents in batches...")
    
    # Process documents in batches to respect token limits
    vector_store = None
    processed_count = 0
    
    for i in range(0, len(validated_documents), batch_size):
        batch = validated_documents[i:i + batch_size]
        
        # Calculate batch token count
        batch_tokens = sum(count_tokens(doc.page_content) for doc in batch)
        
        # If batch exceeds token limit, process smaller chunks
        if batch_tokens > max_tokens_per_batch:
            # Split batch further
            smaller_batches = _split_batch_by_tokens(batch, max_tokens_per_batch)
            
            for small_batch in smaller_batches:
                vector_store = _process_document_batch(
                    small_batch, embeddings, persist_directory, vector_store
                )
                processed_count += len(small_batch)
                print(f"Processed batch: {len(small_batch)} docs, Total: {processed_count}/{len(validated_documents)}")
                time.sleep(1)  # Rate limiting
        else:
            # Process normal batch
            vector_store = _process_document_batch(
                batch, embeddings, persist_directory, vector_store
            )
            processed_count += len(batch)
            print(f"Processed batch: {len(batch)} docs, Total: {processed_count}/{len(validated_documents)}")
            time.sleep(0.5)  # Rate limiting
    
    print(f"Vector store created with {processed_count} documents and persisted to {persist_directory}")
    return vector_store


def _split_batch_by_tokens(documents: List[Document], max_tokens: int) -> List[List[Document]]:
    """Split a batch of documents by token count"""
    batches = []
    current_batch = []
    current_tokens = 0
    
    for doc in documents:
        doc_tokens = count_tokens(doc.page_content)
        
        if current_tokens + doc_tokens > max_tokens and current_batch:
            # Start new batch
            batches.append(current_batch)
            current_batch = [doc]
            current_tokens = doc_tokens
        else:
            current_batch.append(doc)
            current_tokens += doc_tokens
    
    if current_batch:
        batches.append(current_batch)
    
    return batches


def _process_document_batch(documents: List[Document], embeddings, persist_directory: str, 
                          existing_store) -> Chroma:
    """Process a single batch of documents with retry logic"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            if existing_store is None:
                # Create new vector store
                vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=embeddings,
                    persist_directory=persist_directory
                )
            else:
                # Add to existing vector store
                existing_store.add_documents(documents)
                vector_store = existing_store
            
            return vector_store
            
        except Exception as e:
            if "token" in str(e).lower() and attempt < max_retries - 1:
                print(f"Token limit error on attempt {attempt + 1}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Error processing batch: {e}")
                if attempt == max_retries - 1:
                    raise
    
    return existing_store

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