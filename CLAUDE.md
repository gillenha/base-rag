# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) chatbot system designed as a personalized business coach based on Ramit Sethi's Earnable course content. The system processes PDF transcripts from the Earnable course, builds a vector database for efficient retrieval, and provides conversational coaching through a terminal interface.

## Core Architecture

The system consists of several key components:

- **Document Processing Pipeline**: `src/index_documents.py` loads and chunks PDF content from the Earnable course materials
- **Semantic Chunking System**: `src/utils/semantic_chunker.py` preserves framework boundaries and conceptual coherence
- **Vector Store**: Uses ChromaDB with OpenAI embeddings for document retrieval (`src/utils/vector_store.py`)
- **Context-Aware Prompting**: `src/utils/context_aware_prompting.py` adapts responses based on query intent and content type
- **Coaching Context Injection**: `src/utils/coaching_context_injector.py` personalizes responses based on user progress
- **RAG Chain**: LangChain-based conversational retrieval system with dynamic prompting (`src/utils/rag_chain.py`)
- **Chat Interface**: Rich terminal interface with markdown rendering and source display (`src/chat.py`)
- **User Profile System**: Tracks and learns user business information across conversations (`src/utils/user_profile.py`)
- **Document Classification**: `src/utils/document_classifier.py` intelligently categorizes content for enhanced retrieval
- **Ramit Analyzer**: `src/utils/ramit_analyzer.py` enhances content with Ramit-specific coaching patterns
- **Enhanced Retrieval**: `src/utils/ramit_retriever.py` provides context-aware content retrieval with Ramit-specific scoring

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
# Index course content with Ramit-specific semantic enhancement (must be run first)
python src/index_documents.py

# Reindex after updating PDFs (handles duplicates/corrections automatically)
# This will automatically apply Ramit-specific analysis to all chunks
python src/index_documents.py

# Add resume to vector database
python src/add_resume.py path/to/your/resume.pdf

# Add client documents with metadata
python src/add_client_documents.py client_name --client_dir src/data/clients/client_name

# Test enhanced RAG system (development)
python test_enhanced_rag.py

# Test semantic chunking system (development)
python test_semantic_chunking.py
```

### Chat Interface
```bash
# Start basic chat (now auto-saves and shows sources by default)
python src/chat.py chat

# Chat with specific OpenAI model
python src/chat.py chat --model-name gpt-4

# Disable auto-save and source display
python src/chat.py chat --no-autosave --no-show-sources

# Save conversation to markdown file (in addition to autosave)
python src/chat.py chat --save-to-file output.md

# Legacy auto-save mode (saves each response as separate file)
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

## Context-Aware Prompting System

The system uses advanced context-aware prompting to adapt Ramit's coaching style based on query intent and retrieved content:

### Query Intent Classification
- **First Sale**: Queries about getting initial customers
- **Customer Research**: Questions about understanding target audience
- **Pricing**: Discussions about rates and value positioning
- **Frameworks**: Requests for systematic approaches
- **Contrarian**: Challenges to conventional wisdom
- **Tactical**: Need for specific steps and scripts
- **Case Studies**: Requests for examples and stories

### Coaching Style Adaptation
- **Framework-Focused**: Systematic, step-by-step methodologies
- **Contrarian Challenge**: Challenges conventional thinking
- **Tactical Execution**: Specific scripts and actionable steps
- **Mindset Shift**: Addresses psychology and limiting beliefs
- **Case Study Driven**: Uses real student examples
- **Direct Teaching**: Clear principles and core concepts

### Ramit Voice Patterns
The system incorporates Ramit's distinctive language patterns:
- Contrarian openers: "Here's where most people get this wrong..."
- Framework introductions: "Here's the exact framework I use..."
- Tactical language: "Use this exact script..."
- Signature phrases: "Business isn't magic. It's math."

### User Context Integration
Responses adapt based on:
- Current business stage (idea, validation, first sale, scaling, optimizing)
- Completed frameworks and progress indicators
- Previous conversation topics and challenges
- Personal business information from profile

### Configuration Options
```bash
# Enable context-aware prompting (default)
python src/chat.py chat --use-context-aware-prompting

# Disable for testing (uses static prompts)
python src/chat.py chat --no-context-aware-prompting
```

## Testing and Development

### Core Testing Commands
```bash
# Run comprehensive test suite (all tests)
python test_suite/run_all_tests.py --all

# Run specific test categories
python test_suite/run_all_tests.py --comprehensive --regression
python test_suite/run_all_tests.py --categories framework tactical

# Quick validation during development
python test_suite/run_all_tests.py --quick

# Individual test scripts
python test_greeting.py
python test_enhanced_rag.py
python test_semantic_chunking.py
python test_context_aware_prompting.py
python test_document_classification.py
python test_retrieval_quality.py
python test_chat_scenarios.py
```

### Quality and Performance Testing
```bash
# Comprehensive quality validation
python test_suite/comprehensive_test_suite.py

# Multi-turn conversation testing
python test_suite/multi_turn_testing.py

# Regression testing
python test_suite/regression/regression_tests.py

# Before/after comparison
python test_suite/comparison/before_after_comparison.py
```

### Environment Setup
```bash
# Create virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install -r requirements.txt

# Environment variables required
export OPENAI_API_KEY=your_api_key_here
export COURSE_CONTENT_DIR="./01 playbooks"
```

### Development Debugging
```bash
# Debug date parsing issues
python debug_dates.py

# Test specific functionality
python test_greeting.py

# Check system status
python -c "
import os
print('API Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')
print('Vector Store:', 'EXISTS' if os.path.exists('./chroma_db') else 'MISSING')
"
```

## Comprehensive Test Suite

The system includes a sophisticated testing framework located in `test_suite/` that provides multi-dimensional quality assessment:

### Test Suite Structure
- **`test_suite/run_all_tests.py`**: Main test orchestrator that runs all test components
- **`test_suite/comprehensive_test_suite.py`**: End-to-end quality validation across all query types
- **`test_suite/multi_turn_testing.py`**: Validates conversation flow and context retention
- **`test_suite/regression/regression_tests.py`**: Ensures system performance and functionality stability
- **`test_suite/comparison/before_after_comparison.py`**: Quantifies improvements from enhancements
- **`test_suite/monitoring/quality_monitor.py`**: Continuous quality tracking for production
- **`test_suite/metrics/quality_metrics.py`**: Response quality analysis system

### Quality Metrics
The test suite evaluates responses across five key dimensions:
- **Ramit Authenticity (25% weight)**: Captures Ramit's voice and coaching style
- **Framework Coherence (25% weight)**: Accurate representation of methodologies
- **Actionability (20% weight)**: Implementable guidance and specific steps
- **Source Accuracy (15% weight)**: How well responses are supported by retrieved content
- **Coaching Effectiveness (15% weight)**: Ability to guide user thinking forward

### Test Categories
- **Framework Queries**: Tests understanding of Ramit's specific methodologies
- **Tactical Queries**: Tests actionable guidance and implementation steps
- **Mindset Queries**: Tests psychology and invisible scripts coaching
- **Contrarian Queries**: Tests ability to challenge conventional wisdom
- **First Sale Queries**: Tests specific guidance for getting initial customers
- **Pricing Queries**: Tests value positioning and pricing psychology

### Usage Examples
```bash
# Run all tests with comprehensive reporting
python test_suite/run_all_tests.py --all

# Run specific test categories
python test_suite/run_all_tests.py --categories framework tactical mindset

# Quick validation (subset of tests)
python test_suite/run_all_tests.py --quick

# Individual test components
python test_suite/comprehensive_test_suite.py
python test_suite/multi_turn_testing.py
python test_suite/regression/regression_tests.py
```

## Architecture Deep Dive

### Core Data Flow
1. **Document Ingestion**: PDFs → **semantic chunking** → **Ramit-specific analysis** → enhanced metadata → embeddings → ChromaDB
2. **Query Processing**: User input → profile enhancement → **Ramit-enhanced retrieval** → LLM reasoning → response
3. **Profile Learning**: Conversation analysis → business info extraction → JSON storage
4. **Greeting Generation**: Chat logs analysis → theme identification → personalized welcome

### Enhanced Document Processing Pipeline
1. **Semantic Chunking**: Framework-aware chunking preserves conceptual coherence and tactical sequences
2. **Hierarchical Structure**: Creates macro chunks (complete frameworks), micro chunks (tactical steps), and context chunks (transitions)
3. **Boundary Detection**: Identifies framework starts/ends, case study boundaries, and section breaks
4. **Quality Scoring**: Evaluates chunk completeness, framework coherence, and tactical integrity
5. **Ramit Analysis**: Content tagged with primary type (framework, contrarian, tactical, case_study, etc.)
6. **Enhanced Retrieval**: Query classification enables prioritization of relevant Ramit content types

### Key Architectural Patterns
- **Modular Utils**: All business logic isolated in `src/utils/` modules
- **Semantic Chunking**: `semantic_chunker.py` preserves framework coherence and conceptual boundaries
- **Layered Processing**: PDF loading → **semantic chunking** → **Ramit analysis** → embedding → storage
- **Hierarchical Chunks**: Macro (frameworks), micro (tactics), and context (transitions) chunks
- **Quality Metrics**: Conceptual completeness, framework coherence, and tactical integrity scoring
- **Enhanced Retrieval**: `ramit_retriever.py` prioritizes content based on Ramit-specific scoring
- **Context Injection**: User profile data automatically injected into all queries
- **Rich Terminal UI**: Markdown rendering with styled panels and source attribution
- **Conversation Memory**: LangChain's ConversationalRetrievalChain preserves context across interactions

### Vector Database Design
- **ChromaDB**: Persistent vector store with automatic management
- **Enhanced Metadata**: Each chunk includes semantic quality scores and Ramit-specific tags
- **Hierarchical Chunks**: Three chunk types (macro/micro/context) with quality metrics
- **Semantic Quality Fields**: `semantic_quality_score`, `conceptual_completeness`, `framework_coherence`, `tactical_integrity`
- **Metadata-Driven Retrieval**: Document type filtering enables different retrieval behaviors
- **Multi-Document Support**: Course content, resume, and client documents with distinct handling
- **Ramit-Specific Fields**: `ramit_primary_type`, `ramit_frameworks`, `ramit_signatures`, and scoring metrics
- **Source Attribution**: Rich metadata preserved for response citations including Ramit enhancement data

## Common Issues and Solutions

### Vector Database Updates
- **Problem**: Modified or corrected PDF files not reflected in responses
- **Solution**: Run `python src/index_documents.py` to reindex all documents
- **Note**: ChromaDB automatically handles duplicates and updates existing entries

### Chat Interface Troubleshooting
- **Default Behavior**: Chat now auto-saves responses and shows sources by default
- **Saved Files**: All responses automatically saved to `chat_logs/YYYYMMDD_HHMMSS.md`
- **Source Attribution**: Sources grouped by document type (course content, resume, client documents)

### Environment Setup Issues
- **Missing API Key**: Ensure `OPENAI_API_KEY` is set in `.env` file
- **Vector Store Missing**: Run document indexing before starting chat
- **Import Errors**: Activate virtual environment and install requirements

## Development Notes

- The chat interface uses Rich library for terminal formatting and markdown rendering
- ConversationalRetrievalChain maintains conversation memory across interactions
- Source attribution groups and displays references by document type
- The system is designed to be conversational and coaching-focused rather than purely informational
- Environment variables must be set in `.env` file for OpenAI API access
- Vector store persistence handled automatically by ChromaDB
- Python 3.8+ required with virtual environment recommended
- All chat responses automatically include source citations for transparency

## Current Development Status

The system includes several recent enhancements currently in development:

### Recent Improvements
- **Enhanced Document Processing**: Improved PDF loading and chunking with better error handling
- **Advanced Retrieval**: Context-aware retrieval system with Ramit-specific scoring algorithms
- **Document Classification**: Intelligent content categorization for better retrieval targeting
- **Comprehensive Testing**: Multi-dimensional quality assessment framework
- **Performance Monitoring**: Quality tracking and regression testing capabilities

### Active Development Areas
- **Semantic Chunking**: Framework-aware content segmentation that preserves conceptual coherence
- **Ramit Enhancement**: Content analysis and tagging with Ramit-specific coaching patterns
- **Context-Aware Prompting**: Dynamic prompt adaptation based on query intent and content type
- **Retrieval Quality**: Advanced retrieval quality assessment and optimization

### File Status
Recent modifications include:
- `src/index_documents.py`: Enhanced document processing pipeline
- `src/utils/pdf_loader.py`: Improved PDF loading with better error handling  
- `src/utils/ramit_retriever.py`: Context-aware retrieval with Ramit-specific scoring
- `src/utils/document_classifier.py`: New document classification system
- Various test files for quality validation and regression testing

### Dependencies
Core dependencies include:
- `langchain>=0.0.267` with OpenAI and ChromaDB integrations
- `chromadb>=0.4.14` for vector storage and retrieval
- `rich>=13.5.2` for terminal interface formatting
- `typer>=0.9.0` for CLI interface
- `sentence-transformers>=2.2.2` for embeddings
- `pypdf>=3.15.1` for PDF document processing