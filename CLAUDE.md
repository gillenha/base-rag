# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) chatbot system designed as a personalized business coach based on Ramit Sethi's Earnable course content. The system processes PDF transcripts from the Earnable course, builds a vector database for efficient retrieval, and provides conversational coaching through a terminal interface.

## Core Architecture

The system consists of several key components:

- **Document Processing Pipeline**: `src/index_documents.py` loads and chunks PDF content from the Earnable course materials
- **Vector Store**: Uses ChromaDB with OpenAI embeddings for document retrieval (`src/utils/vector_store.py`)
- **RAG Chain**: LangChain-based conversational retrieval system with memory (`src/utils/rag_chain.py`)
- **Chat Interface**: Rich terminal interface with markdown rendering and source display (`src/chat.py`)
- **User Profile System**: Tracks and learns user business information across conversations (`src/utils/user_profile.py`)

## Key Commands

### Setup and Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with:
OPENAI_API_KEY=your_openai_api_key_here
COURSE_CONTENT_DIR=./01 playbooks
```

### Document Indexing
```bash
# Index course content (must be run first)
python src/index_documents.py

# Add resume to vector database
python src/add_resume.py path/to/your/resume.pdf

# Add client documents with metadata
python src/add_client_documents.py client_name --client_dir src/data/clients/client_name
```

### Chat Interface
```bash
# Start basic chat
python src/chat.py chat

# Chat with specific OpenAI model
python src/chat.py chat --model-name gpt-4

# Show document sources in responses
python src/chat.py chat --show-sources

# Save conversation to markdown file
python src/chat.py chat --save-to-file output.md

# Auto-save mode (saves each response as separate file)
python src/chat.py autosave --log-dir ./chat_logs
```

## Document Types and Metadata System

The system handles three distinct document types with different retrieval behaviors:

1. **Course Content** (`document_type` not specified): Main Earnable course materials, freely used for coaching advice
2. **Personal Resume** (`document_type = "resume"`): User's background info, only referenced when contextually relevant
3. **Client Documents** (`document_type = "client_document"`): Specific client project files with rich metadata including:
   - `client_name`: Client identifier
   - `document_category`: Type of document (proposal, strategy, etc.)
   - `project_stage`: Current phase of client work
   - `content_types`: Document content classification
   - `priority`: Relevance ranking

## User Profile Learning

The system automatically extracts and stores business information from conversations:
- Services offered
- Pricing discussed
- Business challenges
- Client situations
- Progress updates

Profile data is stored in `user_profile.json` and used to personalize future coaching responses.

## Development Notes

- The chat interface uses Rich library for terminal formatting and markdown rendering
- ConversationalRetrievalChain maintains conversation memory across interactions
- Source attribution groups and displays references by document type
- The system is designed to be conversational and coaching-focused rather than purely informational
- Environment variables must be set in `.env` file for OpenAI API access
- Vector store persistence handled automatically by ChromaDB