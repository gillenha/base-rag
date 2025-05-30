# Earnable RAG Assistant

A Python-based RAG (Retrieval-Augmented Generation) pipeline that allows you to have interactive conversations with your Earnable course content through a terminal interface.

## Features

- Processes PDF transcripts from the Earnable course
- Builds a vector database for efficient retrieval
- Provides a user-friendly terminal interface
- Retrieves relevant information from your course content
- Shows sources for each response

## Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone this repository:
```
git clone <repository-url>
cd earnable-rag
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Set up your OpenAI API key in the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
COURSE_CONTENT_DIR=./01 playbooks
```

### Indexing Your Course Content

Before you can chat with your course content, you need to index your PDF files:

```
python src/index_documents.py
```

This will:
1. Load all PDF files from the specified directory
2. Split them into chunks
3. Generate embeddings
4. Store them in a vector database

The indexing process may take some time depending on the number and size of your PDF files.

## Usage

After indexing your content, start the chat interface:

```
python src/chat.py
```

You can now have conversations with your course content by typing questions or prompts.

## Advanced Options

You can customize the chat experience with these options:

- Change the OpenAI model:
```
python src/chat.py --model-name gpt-4
```

- Specify a different vector store path:
```
python src/chat.py --vector-store-path ./my_custom_db
```

- Show the sources used for each response:
```
python src/chat.py --show-sources
```

## Adding Your Resume to the Vector Database

You can add your resume to the vector database to provide the assistant with more context about your background and skills:

```
python src/add_resume.py path/to/your/resume.pdf
```

This will:
1. Process your resume document
2. Add appropriate metadata tags
3. Add it to the existing vector database
4. Enable the assistant to reference your background information when relevant

Supported resume formats:
- PDF (.pdf)
- Text files (.txt)
- Markdown (.md)
- Word documents (.docx)

The assistant will use this information to provide more personalized advice without awkwardly injecting irrelevant resume details into conversations.

## Tips for Effective Queries

- Be specific in your questions
- Provide context about your business situation
- Ask about specific modules or topics from the course
- For follow-up questions, the system will maintain conversation context

## Troubleshooting

- If you encounter errors about missing the vector store, make sure you've run the indexing script first.
- If you see API key errors, check that your OpenAI API key is correctly set in the `.env` file.
- For other issues, ensure all dependencies are installed correctly.

## License

This project is licensed under the MIT License. 