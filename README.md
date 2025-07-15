# Sophisticated Expert RAG Framework

A configurable, intelligent RAG (Retrieval-Augmented Generation) framework that adapts to any expert's teaching methodology, voice patterns, and content structure. Transform expert course content into a sophisticated AI coaching system that maintains the expert's distinctive approach.

## 🌟 Features

### **Expert-Agnostic Configuration**
- **Configurable Expert Profiles**: Define any expert's teaching style, frameworks, and voice patterns
- **Dynamic Content Analysis**: Automatically categorizes content based on expert-specific patterns
- **Adaptive Prompting**: Context-aware response generation that matches the expert's coaching style

### **Sophisticated Content Processing**
- **Semantic Chunking**: Framework-aware content segmentation that preserves conceptual coherence
- **Document Classification**: Intelligent categorization (lessons, Q&A, case studies, behind-the-scenes)
- **Authority Scoring**: Confidence-level assessment for different types of expert guidance
- **Enhanced Metadata**: Rich content tagging with expert-specific signatures and frameworks

### **Context-Aware Intelligence**
- **Query Intent Classification**: Understands what type of guidance the user is seeking
- **Content-Driven Coaching Styles**: Adapts response style based on retrieved content (framework-focused, contrarian, tactical, etc.)
- **User Profile Learning**: Builds understanding of user's business/career context over time
- **Dynamic Retrieval**: Prioritizes relevant content based on query type and teaching context

### **Rich Interactive Experience**
- **Expert Voice Simulation**: Responses that authentically capture the expert's communication style
- **Source Attribution**: Transparent citations with content type grouping
- **Conversation Memory**: Maintains context across multi-turn conversations
- **Terminal UI**: Rich markdown rendering with styled panels and source display

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd sophisticated-rag-framework

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key and content directory
```

### 2. Set Up Expert Configuration

#### Option A: Use Existing Expert (Ramit Sethi Examples)
```bash
# Set environment variable to use Ramit Earnable config
export EXPERT_CONFIG_PATH="config/examples/ramit_earnable_config.yaml"

# Or use Dream Job config
export EXPERT_CONFIG_PATH="config/examples/ramit_dreamjob_config.yaml"
```

#### Option B: Create New Expert Configuration
```bash
# Interactive setup for any expert
python setup_new_expert.py "Your Expert Name"

# Follow the guided prompts to configure:
# - Expert profile and teaching style
# - Content types and signature phrases
# - Frameworks and methodologies
# - Voice patterns and coaching styles
```

### 3. Index Expert Content

```bash
# Place expert content (PDFs) in a directory
mkdir expert_content
# Copy PDFs to expert_content/

# Set content directory in .env
echo "COURSE_CONTENT_DIR=./expert_content" >> .env

# Index the content with expert-specific analysis
python src/index_documents.py
```

### 4. Start Coaching Session

```bash
# Launch interactive chat
python src/chat.py chat

# Chat with specific model
python src/chat.py chat --model-name gpt-4

# Disable auto-features if needed
python src/chat.py chat --no-autosave --no-show-sources
```

## 📋 Configuration Guide

### Expert Profile Structure

```yaml
expert_profile:
  name: "Expert Name"
  teaching_style: "Direct, systematic, framework-driven"
  expertise_domain: "Business/Personal Development/Technology"
  signature_approach: "Systematic frameworks with psychology"

content_types:
  framework:
    description: "Systematic approaches and methodologies"
    weight: 1.0
  
  tactical:
    description: "Step-by-step actionable guidance"
    weight: 0.8
  
  # Add more content types...

signature_phrases:
  framework_indicators:
    - phrase: "here's the exact system"
      content_type: "framework"
      weight: 0.8
  
  # Define expert-specific language patterns...

frameworks:
  expert_framework_name:
    keywords:
      - "framework keyword 1"
      - "framework keyword 2"
    description: "Framework description"

voice_patterns:
  contrarian_openers:
    - "Here's where most people get this wrong:"
    - "Conventional wisdom says X, but that's backwards."
  
  framework_introductions:
    - "Here's the exact framework I use:"
    - "Let me walk you through the system:"
```

## 🛠️ Advanced Usage

### Custom Document Processing

```bash
# Semantic chunking with expert analysis
python src/index_documents.py --semantic-chunking --expert-analysis

# Traditional chunking only
python src/index_documents.py --no-semantic-chunking --no-expert-analysis
```

### Testing and Quality Assurance

```bash
# Run comprehensive test suite
python test_suite/run_all_tests.py --all

# Test specific categories
python test_suite/run_all_tests.py --categories framework tactical

# Quick validation
python test_suite/run_all_tests.py --quick
```

### Configuration Management

```bash
# Validate expert configuration
python setup_new_expert.py validate config/my_expert_config.yaml

# List available configurations
python setup_new_expert.py list-configs

# Switch between experts
export EXPERT_CONFIG_PATH="config/experts/new_expert_config.yaml"
```

## 🏗️ Architecture

### Core Components

```
sophisticated-rag-framework/
├── config/
│   ├── expert_config.yaml          # Template configuration
│   └── examples/
│       ├── ramit_earnable_config.yaml
│       └── ramit_dreamjob_config.yaml
├── src/
│   ├── utils/
│   │   ├── expert_analyzer.py      # Configurable content analysis
│   │   ├── configurable_document_classifier.py
│   │   ├── configurable_context_aware_prompting.py
│   │   ├── configurable_enhanced_retriever.py
│   │   └── ...
│   ├── chat.py                     # Interactive chat interface
│   └── index_documents.py          # Document processing pipeline
├── setup_new_expert.py             # Expert configuration helper
└── test_suite/                     # Comprehensive testing framework
```

### Data Flow

1. **Document Ingestion**: PDFs → **Semantic Chunking** → **Expert Analysis** → Enhanced Metadata → Embeddings → ChromaDB
2. **Query Processing**: User Input → **Query Classification** → **Context-Aware Retrieval** → **Dynamic Prompting** → Expert Response
3. **Learning**: Conversation Analysis → User Profile Updates → Personalized Coaching

### Key Abstractions

- **Expert Analyzer**: Configurable content analysis based on expert-specific patterns
- **Document Classifier**: Teaching context and authority level assessment
- **Context-Aware Prompting**: Dynamic prompt generation matching expert's style
- **Enhanced Retriever**: Intelligent content prioritization using expert metadata

## 🧪 Testing Framework

The system includes comprehensive quality assessment:

### Test Categories
- **Framework Queries**: Tests understanding of systematic methodologies
- **Tactical Queries**: Tests actionable guidance and implementation
- **Mindset Queries**: Tests psychology and mental model coaching
- **Contrarian Queries**: Tests ability to challenge conventional wisdom

### Quality Metrics
- **Expert Authenticity (25%)**: Captures expert's voice and style
- **Framework Coherence (25%)**: Accurate methodology representation
- **Actionability (20%)**: Implementable guidance quality
- **Source Accuracy (15%)**: Content-response alignment
- **Coaching Effectiveness (15%)**: Ability to guide user thinking

### Running Tests

```bash
# Full test suite with reporting
python test_suite/run_all_tests.py --all

# Regression testing
python test_suite/regression/regression_tests.py

# Multi-turn conversation testing
python test_suite/multi_turn_testing.py
```

## 📊 Expert Examples

### Ramit Sethi - Earnable (Business)
- **Focus**: Online business development, customer research, offers, authentic selling
- **Style**: Contrarian, framework-driven, tactical with testing emphasis
- **Frameworks**: Customer Research, Winning Offers, Authentic Selling, Profit Playbook

### Ramit Sethi - Dream Job (Career)
- **Focus**: Career advancement, salary negotiation, interview mastery
- **Style**: Psychology-focused, strategic, confidence-building
- **Frameworks**: Dream Job System, Interview Mastery, Salary Negotiation, Career Psychology

## 🤝 Contributing

1. **New Expert Configurations**: Use `setup_new_expert.py` to create configurations for additional experts
2. **Framework Enhancements**: Submit PRs for core framework improvements
3. **Quality Testing**: Add test cases for new expert configurations
4. **Documentation**: Improve setup guides and usage examples

## 📝 Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
COURSE_CONTENT_DIR=./path/to/expert/content

# Optional
EXPERT_CONFIG_PATH=config/experts/your_expert_config.yaml
```

## 🔧 Troubleshooting

### Common Issues

**Configuration Not Found**
```bash
# Check environment variable
echo $EXPERT_CONFIG_PATH

# Validate configuration
python setup_new_expert.py validate $EXPERT_CONFIG_PATH
```

**Vector Store Missing**
```bash
# Reindex documents
python src/index_documents.py
```

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Debug Mode

```bash
# Enable verbose logging
export DEBUG=1
python src/chat.py chat
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on LangChain, ChromaDB, and OpenAI frameworks
- Inspired by sophisticated expert knowledge systems
- Designed for authentic expert voice preservation and intelligent content retrieval

---

**Transform any expert's knowledge into a sophisticated AI coaching system that preserves their unique methodology and teaching style.** 