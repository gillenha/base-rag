#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.pdf_loader import load_pdfs_from_directory, split_documents
from src.utils.vector_store import create_vector_store

def main():
    """
    Main function to index documents and create a vector store.
    """
    # Load environment variables
    load_dotenv()
    
    # Get the course content directory from environment
    course_content_dir = os.getenv("COURSE_CONTENT_DIR", "./01 playbooks")
    
    print(f"Starting to index documents from {course_content_dir}")
    
    # Load PDF documents
    print("Loading PDF documents...")
    documents = load_pdfs_from_directory(course_content_dir)
    
    if not documents:
        print("No documents found. Please check the directory path.")
        return
    
    print(f"Loaded {len(documents)} documents.")
    
    # Split documents into chunks
    print("Splitting documents into chunks...")
    chunks = split_documents(documents)
    
    # Create vector store
    print("Creating vector store...")
    vector_store = create_vector_store(chunks)
    
    print("Indexing completed successfully!")

if __name__ == "__main__":
    main() 