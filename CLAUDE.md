# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sophisticated, configurable RAG (Retrieval-Augmented Generation) framework that transforms expert course content into intelligent AI coaching systems. The framework preserves each expert's distinctive teaching methodology, voice patterns, and content structure while providing advanced features like semantic chunking, context-aware prompting, and dynamic retrieval. Originally built for Ramit Sethi's courses, it now supports any expert through configuration files.

## Core Architecture

The system consists of configurable components that adapt to any expert:

### Configurable Framework Components
- **Expert Analyzer**: `src/utils/expert_analyzer.py` analyzes content using expert-specific patterns from config files
- **Document Classifier**: `src/utils/configurable_document_classifier.py` categorizes content based on expert's teaching contexts
- **Context-Aware Prompting**: `src/utils/configurable_context_aware_prompting.py` adapts responses to match expert's voice and style
- **Enhanced Retriever**: `src/utils/configurable_enhanced_retriever.py` prioritizes content using expert-specific scoring

### Core Pipeline Components
- **Document Processing**: `src/index_documents.py` loads and processes expert content with configurable analysis
- **Semantic Chunking**: `src/utils/semantic_chunker.py` preserves framework boundaries and conceptual coherence
- **Vector Store**: `src/utils/vector_store.py` uses ChromaDB with OpenAI embeddings for retrieval
- **RAG Chain**: `src/utils/rag_chain.py` LangChain-based conversational system with dynamic prompting
- **Chat Interface**: `src/chat.py` rich terminal interface with markdown rendering and source display
- **User Profile System**: `src/utils/user_profile.py` tracks and learns user context across conversations

### Configuration System
- **Expert Configurations**: `config/expert_config.yaml` (template) and `config/examples/` (expert-specific configs)
- **Setup Helper**: `setup_new_expert.py` interactive script for creating new expert configurations

## Key Commands

### Setup and Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with:
OPENAI_API_KEY=your_openai_api_key_here
COURSE_CONTENT_DIR=./path/to/expert/content
EXPERT_CONFIG_PATH=config/examples/ramit_earnable_config.yaml  # Optional: specify expert config
```

### Expert Configuration Management
```bash
# Create new expert configuration (interactive)
python setup_new_expert.py "Expert Name"

# Validate expert configuration
python setup_new_expert.py validate config/my_expert_config.yaml

# List available expert configurations
python setup_new_expert.py list-configs

# Use specific expert configuration
export EXPERT_CONFIG_PATH="config/examples/ramit_earnable_config.yaml"
export EXPERT_CONFIG_PATH="config/examples/ramit_dreamjob_config.yaml"
```

### Document Indexing
```bash
# Index expert content with configurable semantic enhancement (must be run first)
python src/index_documents.py

# Reindex after updating PDFs or changing expert configuration
python src/index_documents.py

# Add resume to vector database
python src/add_resume.py path/to/your/resume.pdf

# Add client documents with metadata
python src/add_client_documents.py client_name --client_dir src/data/clients/client_name
```

### Chat Interface
```bash
# Start chat with expert coaching (auto-saves and shows sources by default)
python src/chat.py chat

# Chat with specific OpenAI model
python src/chat.py chat --model-name gpt-4

# Chat with specific expert configuration
EXPERT_CONFIG_PATH="config/examples/ramit_dreamjob_config.yaml" python src/chat.py chat

# Disable auto-save and source display
python src/chat.py chat --no-autosave --no-show-sources

# Save conversation to markdown file (in addition to autosave)
python src/chat.py chat --save-to-file output.md

# Legacy auto-save mode (saves each response as separate file)
python src/chat.py autosave --log-dir ./chat_logs
```

### Development and Testing
```bash
# Test expert-specific system components
python test_enhanced_rag.py
python test_semantic_chunking.py
python test_context_aware_prompting.py
python test_document_classification.py
python test_retrieval_quality.py
python test_chat_scenarios.py
```

## Expert Configuration System

The framework uses YAML configuration files to define expert-specific behaviors:

### Expert Profile Configuration
```yaml
expert_profile:
  name: "Expert Name"
  teaching_style: "Direct, systematic, framework-driven"
  expertise_domain: "Business/Career/Technology"
  signature_approach: "Systematic frameworks with psychology"
```

### Content Analysis Configuration
- **Content Types**: Framework, mindset, tactical, contrarian, case_study, etc.
- **Signature Phrases**: Expert-specific language patterns and indicators
- **Frameworks**: Expert's methodologies and their key components
- **Voice Patterns**: Distinctive communication styles (contrarian openers, framework introductions, etc.)
- **Document Classification**: Teaching contexts, authority levels, and source types

### Document Types and Metadata System

The system handles three distinct document types with different retrieval behaviors:

1. **Course Content** (`document_type` not specified): Main expert course materials, freely used for coaching advice
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

The system uses advanced context-aware prompting to adapt the expert's coaching style based on query intent and retrieved content:

### Query Intent Classification
Configurable query intents based on expert's domain (examples from business coaching):
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
- **Case Study Driven**: Uses real examples and success stories
- **Direct Teaching**: Clear principles and core concepts

### Expert Voice Patterns (Configurable)
The system incorporates each expert's distinctive language patterns through configuration:
- **Contrarian Openers**: Expert's way of challenging conventional wisdom
- **Framework Introductions**: How the expert introduces systematic approaches
- **Tactical Language**: Expert's style for providing specific guidance
- **Signature Phrases**: Expert's memorable catchphrases and core principles

### User Context Integration
Responses adapt based on:
- Current stage in the expert's domain (e.g., business stage, career level)
- Completed frameworks and progress indicators
- Previous conversation topics and challenges
- Personal context information from user profile

### Configuration Options
```bash
# Enable context-aware prompting (default)
python src/chat.py chat --use-context-aware-prompting

# Disable for testing (uses static prompts)
python src/chat.py chat --no-context-aware-prompting

# Use specific expert configuration
EXPERT_CONFIG_PATH="config/my_expert_config.yaml" python src/chat.py chat
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
- **Expert Authenticity (25% weight)**: Captures the expert's voice and coaching style
- **Framework Coherence (25% weight)**: Accurate representation of expert methodologies
- **Actionability (20% weight)**: Implementable guidance and specific steps
- **Source Accuracy (15% weight)**: How well responses are supported by retrieved content
- **Coaching Effectiveness (15% weight)**: Ability to guide user thinking forward

### Test Categories (Configurable by Expert Domain)
- **Framework Queries**: Tests understanding of expert's specific methodologies
- **Tactical Queries**: Tests actionable guidance and implementation steps
- **Mindset Queries**: Tests psychology and mental model coaching
- **Contrarian Queries**: Tests ability to challenge conventional wisdom
- **Domain-Specific Queries**: Tests expertise in the expert's specific field

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
1. **Document Ingestion**: PDFs → **semantic chunking** → **expert-specific analysis** → enhanced metadata → embeddings → ChromaDB
2. **Query Processing**: User input → profile enhancement → **expert-enhanced retrieval** → LLM reasoning → response
3. **Profile Learning**: Conversation analysis → domain-specific info extraction → JSON storage
4. **Greeting Generation**: Chat logs analysis → theme identification → personalized welcome

### Enhanced Document Processing Pipeline
1. **Semantic Chunking**: Framework-aware chunking preserves conceptual coherence and expert methodology sequences
2. **Hierarchical Structure**: Creates macro chunks (complete frameworks), micro chunks (tactical steps), and context chunks (transitions)
3. **Boundary Detection**: Identifies framework starts/ends, case study boundaries, and section breaks using expert-specific patterns
4. **Quality Scoring**: Evaluates chunk completeness, framework coherence, and tactical integrity
5. **Expert Analysis**: Content tagged with expert-specific types (framework, contrarian, tactical, case_study, etc.) from configuration
6. **Enhanced Retrieval**: Query classification enables prioritization of relevant expert content types

### Key Architectural Patterns
- **Configuration-Driven**: Expert behavior defined through YAML configuration files, not hardcoded logic
- **Modular Utils**: All business logic isolated in `src/utils/` modules with configurable and legacy versions
- **Semantic Chunking**: `semantic_chunker.py` preserves framework coherence and conceptual boundaries
- **Layered Processing**: PDF loading → **semantic chunking** → **expert analysis** → embedding → storage
- **Hierarchical Chunks**: Macro (frameworks), micro (tactics), and context (transitions) chunks
- **Quality Metrics**: Conceptual completeness, framework coherence, and tactical integrity scoring
- **Enhanced Retrieval**: Configurable retrievers prioritize content based on expert-specific scoring
- **Context Injection**: User profile data automatically injected into all queries
- **Rich Terminal UI**: Markdown rendering with styled panels and source attribution
- **Conversation Memory**: LangChain's ConversationalRetrievalChain preserves context across interactions

### Vector Database Design
- **ChromaDB**: Persistent vector store with automatic management
- **Enhanced Metadata**: Each chunk includes semantic quality scores and expert-specific tags
- **Hierarchical Chunks**: Three chunk types (macro/micro/context) with quality metrics
- **Semantic Quality Fields**: `semantic_quality_score`, `conceptual_completeness`, `framework_coherence`, `tactical_integrity`
- **Metadata-Driven Retrieval**: Document type filtering enables different retrieval behaviors
- **Multi-Document Support**: Course content, resume, and client documents with distinct handling
- **Expert-Specific Fields**: `{expert}_primary_type`, `{expert}_frameworks`, `{expert}_signatures`, and scoring metrics (supports both legacy ramit_ prefix and configurable expert prefixes)
- **Source Attribution**: Rich metadata preserved for response citations including expert enhancement data

## Common Issues and Solutions

### Expert Configuration Issues
- **Problem**: Expert configuration not found or invalid
- **Solution**: Set `EXPERT_CONFIG_PATH` environment variable or validate config with `python setup_new_expert.py validate config_file.yaml`
- **Note**: System falls back to Ramit configuration if no expert config specified

### Vector Database Updates
- **Problem**: Modified PDFs or changed expert configuration not reflected in responses
- **Solution**: Run `python src/index_documents.py` to reindex all documents with current expert configuration
- **Note**: ChromaDB automatically handles duplicates and updates existing entries

### Chat Interface Troubleshooting
- **Default Behavior**: Chat auto-saves responses and shows sources by default
- **Saved Files**: All responses automatically saved to `chat_logs/YYYYMMDD_HHMMSS.md`
- **Source Attribution**: Sources grouped by document type (course content, resume, client documents)
- **Expert Switching**: Change `EXPERT_CONFIG_PATH` and restart chat for different expert behavior

### Environment Setup Issues
- **Missing API Key**: Ensure `OPENAI_API_KEY` is set in `.env` file
- **Vector Store Missing**: Run document indexing before starting chat
- **Import Errors**: Activate virtual environment and install requirements
- **Configuration Loading**: Check that YAML configuration files are valid and accessible

## Development Notes

- The chat interface uses Rich library for terminal formatting and markdown rendering
- ConversationalRetrievalChain maintains conversation memory across interactions
- Source attribution groups and displays references by document type
- The system is designed to be conversational and coaching-focused rather than purely informational
- Environment variables must be set in `.env` file for OpenAI API access
- Vector store persistence handled automatically by ChromaDB
- Python 3.8+ required with virtual environment recommended
- All chat responses automatically include source citations for transparency

## Current Framework Status

The system has been transformed from a Ramit-specific implementation to a sophisticated, configurable expert framework:

### Recent Major Transformation
- **Expert-Agnostic Architecture**: Complete abstraction from Ramit-specific to configurable expert system
- **Configuration System**: YAML-based expert configuration with interactive setup tools
- **Backward Compatibility**: Legacy Ramit components preserved alongside new configurable versions
- **Enhanced Testing**: Multi-dimensional quality assessment framework adapted for any expert
- **Setup Automation**: Interactive `setup_new_expert.py` script for rapid expert onboarding

### Configurable Components Created
- **Expert Analysis**: `src/utils/expert_analyzer.py` - Configurable content analysis replacing Ramit-specific version
- **Document Classification**: `src/utils/configurable_document_classifier.py` - Flexible teaching context detection
- **Context-Aware Prompting**: `src/utils/configurable_context_aware_prompting.py` - Adaptive voice pattern system
- **Enhanced Retrieval**: `src/utils/configurable_enhanced_retriever.py` - Smart content prioritization

### File Status
Major framework files:
- `config/expert_config.yaml`: Template configuration for any expert
- `config/examples/ramit_earnable_config.yaml`: Ramit Earnable course configuration
- `config/examples/ramit_dreamjob_config.yaml`: Ramit Dream Job course configuration
- `setup_new_expert.py`: Interactive expert configuration creation tool
- Updated core pipeline files to use configurable components with fallback to legacy versions

### Dependencies
Core dependencies include:
- `langchain>=0.0.267` with OpenAI and ChromaDB integrations
- `chromadb>=0.4.14` for vector storage and retrieval
- `rich>=13.5.2` for terminal interface formatting
- `typer>=0.9.0` for CLI interface
- `sentence-transformers>=2.2.2` for embeddings
- `pypdf>=3.15.1` for PDF document processing