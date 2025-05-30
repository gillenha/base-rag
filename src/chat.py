#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
import typer
from rich.box import ROUNDED
from rich.style import Style

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.vector_store import load_vector_store
from src.utils.rag_chain import create_rag_chain, format_response
from src.utils.user_profile import UserProfile

# Initialize rich console
console = Console()
app = typer.Typer()

def display_sources(sources):
    """
    Display the sources used in the response.
    """
    if not sources:
        return
    
    console.print("\n[dim]Sources used:[/dim]")
    
    # Group sources by document type
    course_sources = []
    resume_sources = []
    client_sources = {}  # Dictionary to store client sources by client name
    
    for source in sources:
        doc_type = source.get("document_type")
        if doc_type == "resume":
            resume_sources.append(source)
        elif doc_type == "client_document":
            client_name = source.get("client_name", "unknown")
            if client_name not in client_sources:
                client_sources[client_name] = []
            client_sources[client_name].append(source)
        else:
            course_sources.append(source)
    
    # Display course content sources
    for idx, source in enumerate(course_sources[:3]):  # Only show top 3 sources
        module = source.get("module", "Unknown")
        source_file = os.path.basename(source.get("source", "Unknown"))
        console.print(f"[dim]• {module}: {source_file}[/dim]")
    
    if len(course_sources) > 3:
        console.print(f"[dim]+ {len(course_sources) - 3} more course content sources[/dim]")
    
    # Display client document sources if any
    for client_name, sources in client_sources.items():
        # Group client sources by document category
        category_grouped = {}
        for source in sources:
            category = source.get("document_category", "general")
            if category not in category_grouped:
                category_grouped[category] = []
            category_grouped[category].append(source)
        
        console.print(f"[dim]• Client ({client_name}) information:[/dim]")
        for category, category_sources in category_grouped.items():
            # Collect content types across all sources in this category
            all_content_types = set()
            for src in category_sources:
                # Content types are now stored as a comma-separated string
                content_types_str = src.get("content_types", "general")
                # Split by comma and strip whitespace
                for content_type in [ct.strip() for ct in content_types_str.split(",")]:
                    all_content_types.add(content_type)
            
            # Display category with content types and count
            content_types_str = ", ".join(sorted(all_content_types))
            source_files = [os.path.basename(src.get("source", "Unknown")) for src in category_sources]
            unique_files = set(source_files)
            if len(unique_files) <= 2:
                files_str = ", ".join(unique_files)
                console.print(f"[dim]  - {category} ({content_types_str}): {files_str}[/dim]")
            else:
                console.print(f"[dim]  - {category} ({content_types_str}): {len(unique_files)} files[/dim]")
    
    # Display resume sources if any, without showing details
    if resume_sources:
        console.print("[dim]• Personal information (resume)[/dim]")

@app.command()
def chat(
    model_name: str = typer.Option("gpt-4", help="Name of the OpenAI model to use"),
    vector_store_path: str = typer.Option("./chroma_db", help="Path to the vector store"),
    show_sources: bool = typer.Option(False, help="Show source documents used by the assistant"),
    profile_path: str = typer.Option("./user_profile.json", help="Path to user profile JSON file"),
):
    """
    Start a chat session with your course content.
    """
    # Load environment variables
    load_dotenv()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY environment variable is not set.")
        console.print("Please set it in the .env file or as an environment variable.")
        return
    
    # Check if vector store exists
    if not os.path.exists(vector_store_path):
        console.print(f"[bold red]Error:[/bold red] Vector store not found at {vector_store_path}")
        console.print("Please run the indexing script first: python src/index_documents.py")
        return
    
    # Load vector store
    try:
        console.print(f"Loading vector store from {vector_store_path}...")
        vector_store = load_vector_store(vector_store_path)
    except Exception as e:
        console.print(f"[bold red]Error loading vector store:[/bold red] {e}")
        return
    
    # Initialize user profile
    user_profile = UserProfile(profile_path=profile_path)
    
    # Create RAG chain
    rag_chain = create_rag_chain(vector_store, model_name)
    
    # Display welcome message with user profile info if available
    welcome_message = "[bold]Your Business Coach[/bold]\n"
    welcome_message += "I'm here to help you build and grow your business based on the Earnable course principles.\n"
    
    # Add personalized info if we know something about the user
    if user_profile.profile["business_info"]["services"]:
        services = ", ".join(user_profile.profile["business_info"]["services"])
        welcome_message += f"I see you offer {services}. That's great!\n"
    
    if user_profile.profile["business_info"]["pricing"]:
        welcome_message += "I remember we discussed your pricing before.\n"
    
    welcome_message += "Feel free to share your progress, ask questions, or discuss challenges.\n"
    welcome_message += "Type [bold]'exit'[/bold], [bold]'quit'[/bold] to end, or [bold]'profile'[/bold] to see what I know about your business."
    
    console.print(Panel.fit(
        welcome_message,
        box=ROUNDED,
        border_style="blue",
        padding=(1, 2),
        title="Earnable Coach"
    ))
    
    # Start chat loop
    while True:
        # Get user query
        query = console.input("\n[bold blue]You:[/bold blue] ")
        
        # Check if user wants to exit
        if query.lower() in ("exit", "quit"):
            console.print("[bold green]Coach:[/bold green] It was great talking with you. Keep building your business! Goodbye!")
            break
        
        # Check if user wants to see their profile
        if query.lower() == "profile":
            profile_text = user_profile.get_formatted_profile()
            console.print(Panel(
                profile_text,
                title="Your Business Profile",
                border_style="green"
            ))
            continue
        
        # Handle empty query
        if not query.strip():
            continue
        
        try:
            with console.status("[bold]Thinking...[/bold]", spinner="dots"):
                # Inject user profile info into the question for context
                profile_context = user_profile.get_formatted_profile()
                enhanced_query = f"{query}\n\n[User Profile Information: {profile_context}]"
                
                # Get response from RAG chain using invoke instead of __call__
                response = rag_chain.invoke({"question": enhanced_query})
                
                formatted_response = format_response(response)
                
                # Extract information from this exchange and update profile
                user_profile.extract_info_from_message(query, formatted_response["answer"])
            
            # Display response
            console.print("\n[bold green]Coach:[/bold green]", end=" ")
            
            # Split answer into paragraphs for better readability
            paragraphs = formatted_response["answer"].split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if i == 0:
                    # First paragraph displayed on the same line as "Coach:"
                    console.print(paragraph.strip())
                else:
                    # Subsequent paragraphs get proper indentation
                    console.print(f"       {paragraph.strip()}")
            
            # Optionally display sources
            if show_sources:
                display_sources(formatted_response["sources"])
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app() 