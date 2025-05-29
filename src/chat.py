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
    for idx, source in enumerate(sources[:3]):  # Only show top 3 sources
        module = source.get("module", "Unknown")
        source_file = os.path.basename(source.get("source", "Unknown"))
        console.print(f"[dim]• {module}: {source_file}[/dim]")
    
    if len(sources) > 3:
        console.print(f"[dim]+ {len(sources) - 3} more sources[/dim]")

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