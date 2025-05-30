#!/usr/bin/env python3
import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.client_loader import process_client_documents
from src.utils.vector_store import load_vector_store, create_vector_store

def load_metadata_mapping(metadata_file: str) -> dict:
    """
    Load metadata mapping from a JSON file.
    
    Args:
        metadata_file: Path to the metadata JSON file
        
    Returns:
        Dictionary mapping filenames to metadata
    """
    if not os.path.exists(metadata_file):
        print(f"Metadata file not found at {metadata_file}, using automatic detection.")
        return {}
    
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        print(f"Loaded metadata mappings for {len(metadata)} files.")
        return metadata
    except json.JSONDecodeError:
        print(f"Error decoding metadata file {metadata_file}, using automatic detection.")
        return {}
    except Exception as e:
        print(f"Error loading metadata file: {e}, using automatic detection.")
        return {}

def main():
    """
    Add client documents to the existing vector store with proper metadata.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Add client documents to the vector database")
    parser.add_argument("client_name", help="Name of the client (e.g., 'terrapin')")
    parser.add_argument("--client_dir", help="Path to the client documents directory (default: src/data/clients/<client_name>)")
    parser.add_argument("--vector_store_path", default="./chroma_db", help="Path to the vector store")
    parser.add_argument("--metadata_file", help="Path to a JSON file with document metadata (optional)")
    parser.add_argument("--chunk_size", type=int, default=500, help="Size of text chunks (default: 500)")
    parser.add_argument("--chunk_overlap", type=int, default=50, help="Overlap between chunks (default: 50)")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Validate that OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in the .env file or as an environment variable.")
        return
    
    # Set client directory if not provided
    if not args.client_dir:
        args.client_dir = f"src/data/clients/{args.client_name}"
    
    # Check if client directory exists
    if not os.path.exists(args.client_dir):
        print(f"Error: Client directory not found at {args.client_dir}")
        return
    
    # Set default metadata file path if not provided
    if not args.metadata_file:
        default_metadata_file = os.path.join(args.client_dir, "metadata.json")
        if os.path.exists(default_metadata_file):
            args.metadata_file = default_metadata_file
            print(f"Found metadata file at {default_metadata_file}")
    
    # Load metadata mapping
    metadata_mapping = {}
    if args.metadata_file:
        metadata_mapping = load_metadata_mapping(args.metadata_file)
    
    print(f"Starting to process client documents for {args.client_name} from {args.client_dir}")
    
    # Process client documents
    client_chunks = process_client_documents(
        args.client_dir, 
        args.client_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        metadata_mapping=metadata_mapping
    )
    
    if not client_chunks:
        print("No client document chunks were created. Please check the files and try again.")
        return
    
    print(f"Processed {len(client_chunks)} chunks from client documents.")
    
    # Check if vector store exists
    if os.path.exists(args.vector_store_path):
        try:
            # Load existing vector store
            print(f"Loading existing vector store from {args.vector_store_path}...")
            vector_store = load_vector_store(args.vector_store_path)
            
            # Add client document chunks to the existing vector store
            print("Adding client documents to vector store...")
            vector_store.add_documents(client_chunks)
            print(f"Client documents added to vector store at {args.vector_store_path}")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Creating a new vector store with just the client documents...")
            create_vector_store(client_chunks, args.vector_store_path)
    else:
        # Create new vector store with just the client documents
        print(f"Vector store not found at {args.vector_store_path}")
        print("Creating a new vector store with the client documents...")
        create_vector_store(client_chunks, args.vector_store_path)
    
    print("\nClient documents added successfully!")
    print("\nWhen chatting with the assistant, the client information will be")
    print("appropriately contextualized based on its metadata tags.")

if __name__ == "__main__":
    main() 