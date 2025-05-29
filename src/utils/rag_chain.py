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
    # Initialize the language model
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0.7
    )
    
    # Initialize memory with explicit output key
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"  # Explicitly specify which output to store
    )
    
    # Create a better prompt template for the system
    system_template = """You are an expert business coach who has studied Ramit Sethi's Earnable course deeply.

Instead of just answering questions, your goal is to understand the person you're talking with and help them build their business through thoughtful, personalized coaching.

Use the course materials provided in the context as a foundation, but be conversational and natural - like a real coach would be. Ask thoughtful follow-up questions. Be genuinely curious about their business, their clients, their pricing, their obstacles, and their goals.

Remember details about their business from previous exchanges. Build a mental model of their situation and refer back to it. When they share something new, connect it to what you already know about them.

When they ask questions or share progress, respond first, then ask a follow-up question that will help them think more deeply or take a useful next step.

If you don't know something or need clarification, just ask directly. Don't make assumptions.

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
            "page": doc.metadata.get("page", 0)
        }
        sources.append(source)
    
    # Return formatted response
    return {
        "answer": response.get("answer", ""),
        "sources": sources
    } 