from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

def create_rag_chain(vector_store, model_name="gpt-3.5-turbo"):
    """
    Creates a RAG chain that combines retrieval and generation.
    
    Args:
        vector_store: Vector store for retrieval
        model_name: Name of the LLM model to use
        
    Returns:
        A RAG chain
    """
    # Initialize the OpenAI LLM
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0.1  # Lower temperature for more factual, less creative responses
    )
    
    # Initialize memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"  # Explicitly specify which key from chain output to store in memory
                             # This fixes the "Got multiple output keys" error
    )
    
    # Create a better prompt template for the system
    system_template = """You are a knowledge repository trained on Ramit Sethi's Earnable course materials. Your job is to provide accurate, specific information from the course content without coaching, encouragement, or personal commentary.

Answer questions directly using the provided context. State facts, frameworks, and specific steps from the course materials. Do not add motivational language, congratulations, or emotional support.

When answering:
- Cite specific modules, documents, or sections when possible
- Provide exact processes, frameworks, or strategies from the course
- Give direct answers without preamble or encouragement
- If information isn't in the provided context, state that clearly
- Don't ask follow-up questions unless clarification is needed to answer accurately

## Context Handling Instructions:
1. For course content (document_type is not specified), provide information directly from the Earnable materials.
2. For resume information (document_type = "resume"), only reference when directly relevant to the specific question asked.
3. For client information (document_type = "client_document"), provide specific details about that client project when asked.

Your responses should be:
- Direct and factual
- Free of motivational language
- Focused on course-specific information
- Clear about sources and references

Context: {context}
----------------
Chat History: {chat_history}
"""
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # Create RAG chain with custom prompt
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        ),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": chat_prompt},
        verbose=True
    )
    
    return rag_chain

def format_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the response from the RAG chain.
    
    Args:
        response: Response from the RAG chain
        
    Returns:
        Formatted response with answer and sources
    """
    sources = []
    
    # Extract sources from the response
    for doc in response.get("source_documents", []):
        source = {
            "content": doc.page_content[:150] + "...",
            "source": doc.metadata.get("source", "Unknown"),
            "module": doc.metadata.get("module", "Unknown"),
            "page": doc.metadata.get("page", 0),
            "document_type": doc.metadata.get("document_type", "course_content")
        }
        
        # Add client-specific metadata if available
        if source["document_type"] == "client_document":
            source["client_name"] = doc.metadata.get("client_name", "unknown")
            source["document_category"] = doc.metadata.get("document_category", "general")
            source["project_stage"] = doc.metadata.get("project_stage", "undefined")
            source["content_types"] = doc.metadata.get("content_types", "general")
            source["priority"] = doc.metadata.get("priority", 5)
        
        sources.append(source)
    
    # Return formatted response
    return {
        "answer": response.get("answer", ""),
        "sources": sources
    } 