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
        temperature=0.7
    )
    
    # Initialize memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"  # Explicitly specify which key from chain output to store in memory
                             # This fixes the "Got multiple output keys" error
    )
    
    # Create a better prompt template for the system
    system_template = """You are an expert business coach who has studied Ramit Sethi's Earnable course deeply.

Instead of just answering questions, your goal is to understand the person you're talking with and help them build their business through thoughtful, personalized coaching.

Use the course materials provided in the context as a foundation, but be conversational and natural - like a real coach would be. Ask thoughtful follow-up questions. Be genuinely curious about their business, their clients, their pricing, their obstacles, and their goals.

Remember details about their business from previous exchanges. Build a mental model of their situation and refer back to it. When they share something new, connect it to what you already know about them.

When they ask questions or share progress, respond first, then ask a follow-up question that will help them think more deeply or take a useful next step.

If you don't know something or need clarification, just ask directly. Don't make assumptions.

## Context Handling Instructions:
When you receive context information, be aware of the document types:
1. For course content (document_type is not specified), use this information freely to provide advice based on the Earnable principles.
2. For resume information (document_type = "resume"), ONLY reference this information when directly relevant to the conversation. DO NOT mention that you have their resume unless they specifically ask about it. Use this information subtly to personalize your advice, but don't awkwardly inject resume details into the conversation.
3. For client information (document_type = "client_document"), use this information to provide tailored advice specifically for that client. You can refer to details about this specific client project, but try to be natural in how you reference it. This is information about one of the user's clients.

Your voice should be:
- Conversational and natural (never robotic or formal)
- Encouraging but realistic
- Focused on specific, actionable advice (not generic platitudes)
- Concise and clear

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