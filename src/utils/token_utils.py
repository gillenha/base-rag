"""
Token counting utilities for managing OpenAI API limits
"""
import tiktoken
from typing import List


def count_tokens(text: str, model: str = "text-embedding-ada-002") -> int:
    """
    Count tokens in text for a given model
    
    Args:
        text: Text to count tokens for
        model: Model name for tokenizer
        
    Returns:
        Number of tokens
    """
    try:
        # Get the encoding for the model
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4


def chunk_text_by_tokens(text: str, max_tokens: int = 1000, overlap_tokens: int = 100) -> List[str]:
    """
    Chunk text by token count rather than character count
    
    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Overlap between chunks in tokens
        
    Returns:
        List of text chunks
    """
    encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        # Define end position
        end = min(start + max_tokens, len(tokens))
        
        # Extract chunk tokens
        chunk_tokens = tokens[start:end]
        
        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Move start position (with overlap)
        start = end - overlap_tokens
        
        # Prevent infinite loop
        if start >= end:
            break
    
    return chunks


def validate_token_limit(text: str, max_tokens: int = 8000) -> bool:
    """
    Validate that text is under token limit
    
    Args:
        text: Text to validate
        max_tokens: Maximum allowed tokens
        
    Returns:
        True if under limit, False otherwise
    """
    token_count = count_tokens(text)
    return token_count <= max_tokens


def truncate_to_token_limit(text: str, max_tokens: int = 8000) -> str:
    """
    Truncate text to fit within token limit
    
    Args:
        text: Text to truncate
        max_tokens: Maximum allowed tokens
        
    Returns:
        Truncated text
    """
    if validate_token_limit(text, max_tokens):
        return text
    
    encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
    tokens = encoding.encode(text)
    
    # Truncate tokens and decode back
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)