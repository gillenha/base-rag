#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.resume_loader import process_resume
from src.utils.vector_store import load_vector_store, create_vector_store

def main():
    """
    Add a resume document to the existing vector store with proper metadata.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Add a resume document to the vector database")
    parser.add_argument("resume_path", help="Path to the resume file (PDF, TXT, MD, DOCX)")
    parser.add_argument("--vector_store_path", default="./chroma_db", help="Path to the vector store")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Validate that OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in the .env file or as an environment variable.")
        return
    
    # Check if resume file exists
    if not os.path.exists(args.resume_path):
        print(f"Error: Resume file not found at {args.resume_path}")
        return
    
    print(f"Starting to process resume from {args.resume_path}")
    
    # Process resume document
    resume_chunks = process_resume(args.resume_path)
    
    if not resume_chunks:
        print("No resume chunks were created. Please check the file and try again.")
        return
    
    print(f"Processed {len(resume_chunks)} chunks from resume.")
    
    # Check if vector store exists
    if os.path.exists(args.vector_store_path):
        try:
            # Load existing vector store
            print(f"Loading existing vector store from {args.vector_store_path}...")
            vector_store = load_vector_store(args.vector_store_path)
            
            # Add resume chunks to the existing vector store
            print("Adding resume to vector store...")
            vector_store.add_documents(resume_chunks)
            # The persist() method is no longer needed as it's automatically persisted
            print(f"Resume added to vector store at {args.vector_store_path}")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Creating a new vector store with just the resume...")
            create_vector_store(resume_chunks, args.vector_store_path)
    else:
        # Create new vector store with just the resume
        print(f"Vector store not found at {args.vector_store_path}")
        print("Creating a new vector store with the resume...")
        create_vector_store(resume_chunks, args.vector_store_path)
    
    print("\nResume added successfully!")
    print("\nWhen chatting with the assistant, the resume information will be")
    print("appropriately contextualized based on its metadata tags.")

if __name__ == "__main__":
    main() 