import os
import re
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

def detect_document_category(file_path: str, content: str) -> str:
    """
    Automatically detect the document category based on filename and content.
    
    Args:
        file_path: Path to the file
        content: Text content of the document
        
    Returns:
        Document category as a string
    """
    filename = os.path.basename(file_path).lower()
    
    # Check filename patterns
    if any(term in filename for term in ['proposal', 'offer']):
        return 'proposal'
    elif any(term in filename for term in ['contract', 'agreement']):
        return 'contract'
    elif any(term in filename for term in ['report', 'update']):
        return 'report'
    elif any(term in filename for term in ['review', 'feedback']):
        return 'feedback'
    elif any(term in filename for term in ['requirements', 'specs']):
        return 'requirements'
    elif any(term in filename for term in ['contact', 'listing']):
        return 'contact'
    
    # Check content patterns if filename wasn't conclusive
    content_sample = content[:1000].lower()  # Check first 1000 chars
    if 'proposal' in content_sample or 'quote' in content_sample:
        return 'proposal'
    elif 'contract' in content_sample or 'agreement' in content_sample:
        return 'contract'
    elif 'report' in content_sample or 'progress' in content_sample:
        return 'report'
    elif 'feedback' in content_sample or 'review' in content_sample:
        return 'feedback'
    
    # Default category
    return 'general'

def detect_project_stage(file_path: str, content: str) -> str:
    """
    Automatically detect the project stage based on filename and content.
    
    Args:
        file_path: Path to the file
        content: Text content of the document
        
    Returns:
        Project stage as a string
    """
    filename = os.path.basename(file_path).lower()
    
    # Check filename patterns
    if any(term in filename for term in ['initial', 'draft', 'preliminary']):
        return 'initial'
    elif any(term in filename for term in ['final', 'completed', 'delivery']):
        return 'completed'
    elif any(term in filename for term in ['progress', 'update', 'ongoing']):
        return 'in-progress'
    
    # Check content patterns
    content_sample = content[:1000].lower()
    if 'initial' in content_sample or 'start' in content_sample:
        return 'initial'
    elif 'final' in content_sample or 'complete' in content_sample:
        return 'completed'
    elif 'progress' in content_sample or 'ongoing' in content_sample:
        return 'in-progress'
    
    # Default stage
    return 'undefined'

def detect_content_types(content: str) -> List[str]:
    """
    Detect the types of content in the document.
    
    Args:
        content: Text content of the document
        
    Returns:
        List of content types found in the document
    """
    content_types = []
    content_lower = content.lower()
    
    # Detect pricing information
    price_patterns = [
        r'\$\s*\d+[\d,.]*',
        r'pricing',
        r'cost',
        r'budget',
        r'payment',
        r'invoice'
    ]
    if any(re.search(pattern, content_lower) for pattern in price_patterns):
        content_types.append('pricing')
    
    # Detect service descriptions
    service_patterns = [
        r'service',
        r'offer',
        r'provide',
        r'deliverable',
        r'include',
        r'feature'
    ]
    if any(re.search(pattern, content_lower) for pattern in service_patterns):
        content_types.append('services')
    
    # Detect technical details
    tech_patterns = [
        r'technical',
        r'specification',
        r'requirement',
        r'architecture',
        r'system',
        r'platform'
    ]
    if any(re.search(pattern, content_lower) for pattern in tech_patterns):
        content_types.append('technical')
    
    # Detect testimonials or client feedback
    feedback_patterns = [
        r'review',
        r'testimonial',
        r'feedback',
        r'recommend',
        r'happy with',
        r'satisfied'
    ]
    if any(re.search(pattern, content_lower) for pattern in feedback_patterns):
        content_types.append('testimonials')
    
    # Detect timeline information
    timeline_patterns = [
        r'timeline',
        r'schedule',
        r'deadline',
        r'milestone',
        r'due date',
        r'delivery date'
    ]
    if any(re.search(pattern, content_lower) for pattern in timeline_patterns):
        content_types.append('timeline')
    
    # If no specific types were detected
    if not content_types:
        content_types.append('general')
    
    return content_types

def load_client_document(
    file_path: str, 
    client_name: str,
    document_category: Optional[str] = None,
    project_stage: Optional[str] = None,
    content_types: Optional[List[str]] = None,
    priority: int = 5  # 1-10 scale, 10 being highest
) -> List[Document]:
    """
    Loads a client document file (PDF, TXT, etc.) and adds appropriate metadata.
    
    Args:
        file_path: Path to the client document file
        client_name: Name of the client (e.g., 'terrapin')
        document_category: Category of document (proposal, contract, feedback, etc.)
        project_stage: Stage of the project (initial, in-progress, completed)
        content_types: Types of content in the document (pricing, services, technical, etc.)
        priority: Importance of the document (1-10)
        
    Returns:
        List of document chunks with client-specific metadata
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
        client_documents = loader.load()
        
        # If no document found
        if not client_documents:
            print(f"Warning: No content loaded from {file_path}")
            return []
        
        # Get combined content for auto-detection
        combined_content = "\n".join([doc.page_content for doc in client_documents])
        
        # Auto-detect metadata if not provided
        if document_category is None:
            document_category = detect_document_category(file_path, combined_content)
        
        if project_stage is None:
            project_stage = detect_project_stage(file_path, combined_content)
        
        if content_types is None:
            content_types = detect_content_types(combined_content)
        
        # Convert content types to string for ChromaDB compatibility
        content_types_str = ", ".join(content_types)
        
        # Add metadata to each document
        for doc in client_documents:
            doc.metadata["source"] = file_path
            doc.metadata["filename"] = os.path.basename(file_path)
            doc.metadata["document_type"] = "client_document"
            doc.metadata["client_name"] = client_name
            doc.metadata["document_category"] = document_category
            doc.metadata["project_stage"] = project_stage
            doc.metadata["content_types"] = content_types_str  # Store as string, not list
            doc.metadata["priority"] = priority
            
        documents.extend(client_documents)
        print(f"Loaded client document: {file_path}")
        print(f"  Category: {document_category}, Stage: {project_stage}")
        print(f"  Content Types: {content_types_str}, Priority: {priority}")
        
    except Exception as e:
        print(f"Error loading client document {file_path}: {e}")
    
    return documents

def load_client_documents_from_directory(
    directory_path: str, 
    client_name: str,
    metadata_mapping: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Document]:
    """
    Recursively loads all document files from a client directory.
    
    Args:
        directory_path: Path to the client document directory
        client_name: Name of the client (e.g., 'terrapin')
        metadata_mapping: Optional dictionary mapping filenames to metadata
            Example: {
                "proposal.pdf": {
                    "document_category": "proposal",
                    "project_stage": "initial",
                    "content_types": ["pricing", "services"],
                    "priority": 8
                }
            }
        
    Returns:
        List of documents with client-specific metadata
    """
    documents = []
    metadata_mapping = metadata_mapping or {}
    
    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.pdf', '.txt', '.md', '.docx')) and not file.startswith('._'):
                try:
                    file_path = os.path.join(root, file)
                    
                    # Check if we have predefined metadata for this file
                    file_metadata = metadata_mapping.get(file, {})
                    
                    client_docs = load_client_document(
                        file_path, 
                        client_name,
                        document_category=file_metadata.get("document_category"),
                        project_stage=file_metadata.get("project_stage"),
                        content_types=file_metadata.get("content_types"),
                        priority=file_metadata.get("priority", 5)
                    )
                    documents.extend(client_docs)
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    
    return documents

def process_client_documents(
    directory_path: str, 
    client_name: str, 
    chunk_size: int = 500, 
    chunk_overlap: int = 50,
    metadata_mapping: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Document]:
    """
    Loads and processes all documents for a specific client, splitting them into chunks with metadata.
    
    Args:
        directory_path: Path to the client document directory
        client_name: Name of the client (e.g., 'terrapin')
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        metadata_mapping: Optional dictionary mapping filenames to metadata
        
    Returns:
        List of processed document chunks
    """
    # Load all client documents
    documents = load_client_documents_from_directory(
        directory_path, 
        client_name,
        metadata_mapping=metadata_mapping
    )
    
    if not documents:
        print("No client documents loaded. Please check the directory path.")
        return []
    
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Ensure all chunks have the client metadata
    for chunk in chunks:
        # Make sure each chunk preserves the important metadata
        chunk.metadata["document_type"] = "client_document"
        chunk.metadata["client_name"] = client_name
        
        # Ensure these fields exist, even if they weren't in the original metadata
        if "document_category" not in chunk.metadata:
            chunk.metadata["document_category"] = "general"
        if "project_stage" not in chunk.metadata:
            chunk.metadata["project_stage"] = "undefined"
        if "content_types" not in chunk.metadata:
            chunk.metadata["content_types"] = "general"  # String, not list
        if "priority" not in chunk.metadata:
            chunk.metadata["priority"] = 5
    
    print(f"Split client documents into {len(chunks)} chunks")
    
    return chunks 