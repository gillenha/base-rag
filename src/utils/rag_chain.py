from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.base import Chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema.runnable import Runnable
from .configurable_context_aware_prompting import create_expert_prompt_generator, UserContext
from .coaching_context_injector import create_coaching_context_injector

def create_rag_chain(vector_store, model_name="gpt-3.5-turbo", use_context_aware_prompting=True, expert_config_path=None):
    """
    Creates a RAG chain that combines retrieval and generation with context-aware prompting.
    
    Args:
        vector_store: Vector store for retrieval
        model_name: Name of the LLM model to use
        use_context_aware_prompting: Whether to use dynamic prompting based on query context
        expert_config_path: Path to expert configuration file
        
    Returns:
        A RAG chain with context-aware prompting capabilities
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
    
    # Initialize context-aware prompting components if enabled
    if use_context_aware_prompting:
        prompt_generator = create_expert_prompt_generator(expert_config_path)
        context_injector = create_coaching_context_injector()
        print("Using context-aware prompting for dynamic response adaptation")
        
        # Create a simple template for context-aware prompting
        # The actual prompt will be generated dynamically by the prompt_generator
        system_template = "{context_aware_prompt}"
        chat_prompt = PromptTemplate(
            input_variables=["context_aware_prompt"],
            template=system_template
        )
    else:
        # Fallback to static prompt template
        system_template = """You are a knowledge repository specifically trained on expert course materials. Your job is to provide the expert's specific frameworks, methodologies, and distinctive approaches rather than generic advice.

When answering questions, prioritize content that contains:
- The expert's specific frameworks and methodologies
- Their distinctive takes and approaches
- Tactical, step-by-step processes from the course
- Real case studies and examples
- Specific metrics and practical approaches
- The expert's distinctive teaching style and content

## Response Guidelines:
- Use the expert's terminology and specific frameworks when available
- Reference their distinctive approaches when they apply
- Include tactical steps and exact processes
- Cite specific modules, documents, or sections
- Highlight unique perspectives that differ from conventional advice
- Present information as the expert teaches it, not as generic content

## Context Handling Instructions:
1. For course content (document_type is not specified), prioritize content with high framework_score, contrarian_score, or tactical_score
2. For resume information (document_type = "resume"), only reference when directly relevant
3. For client information (document_type = "client_document"), provide specific details about that client project when asked

Look for these expert-specific content indicators in the context:
- primary_type: The main type of expert content (framework, contrarian, tactical, etc.)
- frameworks: Specific frameworks mentioned
- signatures: Key phrases that indicate the expert's specific approach
- scores: Higher scores indicate content strength in various categories

Context: {context}
----------------
Chat History: {chat_history}"""
        
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "{question}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # Create enhanced retriever with expert-specific logic
    try:
        from .configurable_enhanced_retriever import create_expert_enhanced_retriever
        retriever = create_expert_enhanced_retriever(vector_store, expert_config_path, {"k": 5})
        print("Using expert-enhanced retriever for better semantic matching")
    except ImportError:
        print("Expert-enhanced retriever not available, using standard retriever")
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
    
    # Create RAG chain with custom prompt and enhanced retriever
    if use_context_aware_prompting:
        # Create a custom RAG chain that generates prompts dynamically
        rag_chain = ContextAwareRAGChain(
            llm=llm,
            retriever=retriever,
            memory=memory,
            prompt_generator=prompt_generator,
            context_injector=context_injector,
            return_source_documents=True,
            verbose=True
        )
    else:
        # Use standard ConversationalRetrievalChain
        rag_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": chat_prompt},
            verbose=True
        )
    
    return rag_chain

class ContextAwareRAGChain:
    """
    Custom RAG chain that generates context-aware prompts dynamically based on
    query intent, retrieved content, and user context.
    """
    
    def __init__(self, llm, retriever, memory, prompt_generator, context_injector, 
                 return_source_documents=True, verbose=False):
        self.llm = llm
        self.retriever = retriever
        self.memory = memory
        self.prompt_generator = prompt_generator
        self.context_injector = context_injector
        self.return_source_documents = return_source_documents
        self.verbose = verbose
    
    @property
    def input_keys(self) -> List[str]:
        """Input keys for the chain"""
        return ["question"]
    
    @property
    def output_keys(self) -> List[str]:
        """Output keys for the chain"""
        return ["answer", "source_documents"] if self.return_source_documents else ["answer"]
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Internal call method required by LangChain Chain interface"""
        return self._process_query(inputs)
    
    def invoke(self, input: Dict[str, Any], config=None, **kwargs) -> Dict[str, Any]:
        """LangChain Runnable interface method"""
        return self._process_query(input)
    
    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process a query with context-aware prompting"""
        return self._process_query(inputs)
    
    def _process_query(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Core query processing logic"""
        query = inputs.get("question", "")
        chat_history = self._get_chat_history()
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.get_relevant_documents(query)
        
        # Convert documents to source format for prompt generation
        sources = []
        for doc in retrieved_docs:
            source = {
                "content": doc.page_content,
                "ramit_type": doc.metadata.get("ramit_primary_type", "general"),
                "ramit_frameworks": doc.metadata.get("ramit_frameworks", "").split(",") if doc.metadata.get("ramit_frameworks") else [],
                "ramit_scores": {
                    "framework": doc.metadata.get("ramit_framework_score", 0),
                    "contrarian": doc.metadata.get("ramit_contrarian_score", 0),
                    "tactical": doc.metadata.get("ramit_tactical_score", 0),
                    "case_study": doc.metadata.get("ramit_case_study_score", 0)
                }
            }
            sources.append(source)
        
        # Load user context from profile and chat history
        try:
            user_context_data = self.context_injector.analyze_user_context()
            business_progress, recent_sessions = user_context_data
            
            user_context = UserContext(
                business_type=None,  # Could be extracted from profile
                experience_level=business_progress.current_stage,
                previous_topics=[topic for session in recent_sessions[:3] for topic in session.topics_discussed],
                current_challenges=business_progress.ongoing_challenges,
                progress_indicators=business_progress.recent_wins
            )
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not load user context: {e}")
            user_context = None
        
        # Generate context-aware prompt
        context_aware_prompt = self.prompt_generator.generate_context_aware_prompt(
            query=query,
            sources=sources,
            user_context=user_context,
            chat_history=chat_history
        )
        
        if self.verbose:
            print(f"Generated context-aware prompt for query intent and content type")
        
        # Generate response using the dynamic prompt
        response = self.llm.predict(context_aware_prompt)
        
        # Store in memory
        self.memory.save_context(
            {"input": query},
            {"answer": response}
        )
        
        # Format response
        result = {
            "question": query,
            "answer": response,
            "chat_history": self.memory.chat_memory.messages
        }
        
        if self.return_source_documents:
            result["source_documents"] = retrieved_docs
        
        return result
    
    def _get_chat_history(self) -> str:
        """Get formatted chat history string"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return ""
        
        # Format recent messages (last 4 for context)
        recent_messages = messages[-4:] if len(messages) > 4 else messages
        formatted_history = []
        
        for message in recent_messages:
            if hasattr(message, 'content'):
                role = "Human" if message.type == "human" else "Assistant"
                formatted_history.append(f"{role}: {message.content}")
        
        return "\n".join(formatted_history)

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
        
        # Add Ramit-specific metadata if available
        ramit_primary_type = doc.metadata.get("ramit_primary_type")
        if ramit_primary_type and ramit_primary_type != "general":
            source["ramit_type"] = ramit_primary_type
            
            # Convert string back to list for display
            frameworks_str = doc.metadata.get("ramit_frameworks", "")
            source["ramit_frameworks"] = frameworks_str.split(",") if frameworks_str else []
            
            signatures_str = doc.metadata.get("ramit_signatures", "")
            source["ramit_signatures"] = signatures_str.split(",") if signatures_str else []
            
            # Add scores for debugging/display
            source["ramit_scores"] = {
                "contrarian": doc.metadata.get("ramit_contrarian_score", 0),
                "tactical": doc.metadata.get("ramit_tactical_score", 0),
                "framework": doc.metadata.get("ramit_framework_score", 0),
                "case_study": doc.metadata.get("ramit_case_study_score", 0)
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