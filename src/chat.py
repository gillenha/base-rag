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
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.vector_store import load_vector_store
from src.utils.rag_chain import create_rag_chain, format_response
from src.utils.user_profile import UserProfile
from src.utils.greeting_generator import GreetingGenerator

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
    show_sources: bool = typer.Option(True, help="Show source documents used by the assistant"),
    profile_path: str = typer.Option("./user_profile.json", help="Path to user profile JSON file"),
    save_to_file: str = typer.Option(None, help="Save conversation to a Markdown file at the specified path"),
    autosave: bool = typer.Option(True, help="Automatically save each response to timestamped files in chat_logs"),
    use_context_aware_prompting: bool = typer.Option(True, help="Use context-aware prompting that adapts to query intent and content"),
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
    rag_chain = create_rag_chain(vector_store, model_name, use_context_aware_prompting)
    
    # Initialize greeting generator
    greeting_generator = GreetingGenerator(chat_logs_dir="./chat_logs", user_profile=user_profile)
    
    # Generate personalized greeting
    greeting_message = greeting_generator.generate_greeting()
    quick_suggestions = greeting_generator.get_quick_start_suggestions()
    
    # Ensure chat_logs directory exists if autosave is enabled
    if autosave:
        os.makedirs("./chat_logs", exist_ok=True)
    
    # Display personalized welcome message
    welcome_panel = f"[bold]Your Business Coach[/bold]\n\n{greeting_message}\n"
    
    if quick_suggestions:
        welcome_panel += "\n[bold]Quick start suggestions:[/bold]\n"
        welcome_panel += "\n".join(quick_suggestions)
        welcome_panel += "\n"
    
    autosave_note = "\nResponses will be automatically saved to chat_logs/" if autosave else ""
    welcome_panel += f"{autosave_note}\nType [bold]'exit'[/bold], [bold]'quit'[/bold] to end, or [bold]'profile'[/bold] to see what I know about your business."
    
    console.print(Panel.fit(
        welcome_panel,
        box=ROUNDED,
        border_style="blue",
        padding=(1, 2),
        title="Earnable Coach"
    ))
    
    # Initialize markdown file if save_to_file is specified
    md_file = None
    if save_to_file:
        # Generate a default filename with timestamp if not provided
        if save_to_file == "auto":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_to_file = f"earnable_coach_{timestamp}.md"
        
        # Create or open the file
        try:
            os.makedirs(os.path.dirname(os.path.abspath(save_to_file)), exist_ok=True)
            md_file = open(save_to_file, "w", encoding="utf-8")
            md_file.write("# Earnable Coach Conversation\n\n")
            md_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            console.print(f"[bold]Saving conversation to[/bold]: {save_to_file}")
        except Exception as e:
            console.print(f"[bold red]Error creating output file:[/bold red] {e}")
            console.print("Continuing without saving to file.")
            md_file = None
    
    # Start chat loop
    while True:
        # Get user query
        query = console.input("\n[bold blue]You:[/bold blue] ")
        
        # Check if user wants to exit
        if query.lower() in ("exit", "quit"):
            console.print("[bold green]Coach:[/bold green] It was great talking with you. Keep building your business! Goodbye!")
            
            # Save exit message to file if enabled
            if md_file:
                md_file.write("\n## You\n\nexit\n\n## Coach\n\nIt was great talking with you. Keep building your business! Goodbye!\n")
                md_file.close()
                console.print(f"[bold]Conversation saved to[/bold]: {save_to_file}")
            
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
        
        # Save user query to file if enabled
        if md_file:
            md_file.write(f"\n## You\n\n{query}\n")
        
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
            console.print("\n[bold green]Coach:[/bold green]")
            
            # Use Markdown rendering for better formatting
            md = Markdown(formatted_response["answer"].strip())
            console.print(md)
            
            # Save response to file if enabled
            if md_file:
                md_file.write(f"\n## Coach\n\n{formatted_response['answer'].strip()}\n")
                
                # Also save sources if they're shown
                if show_sources and formatted_response["sources"]:
                    md_file.write("\n### Sources\n\n")
                    
                    # Group sources by document type
                    course_sources = []
                    resume_sources = []
                    client_sources = {}
                    
                    for source in formatted_response["sources"]:
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
                    
                    # Write course content sources
                    for idx, source in enumerate(course_sources[:3]):
                        module = source.get("module", "Unknown")
                        source_file = os.path.basename(source.get("source", "Unknown"))
                        md_file.write(f"- {module}: {source_file}\n")
                    
                    if len(course_sources) > 3:
                        md_file.write(f"- Plus {len(course_sources) - 3} more course content sources\n")
                    
                    # Write client document sources
                    for client_name, sources in client_sources.items():
                        # Group client sources by document category
                        category_grouped = {}
                        for source in sources:
                            category = source.get("document_category", "general")
                            if category not in category_grouped:
                                category_grouped[category] = []
                            category_grouped[category].append(source)
                        
                        md_file.write(f"- Client ({client_name}) information:\n")
                        for category, category_sources in category_grouped.items():
                            # Collect content types across all sources in this category
                            all_content_types = set()
                            for src in category_sources:
                                content_types_str = src.get("content_types", "general")
                                for content_type in [ct.strip() for ct in content_types_str.split(",")]:
                                    all_content_types.add(content_type)
                            
                            content_types_str = ", ".join(sorted(all_content_types))
                            source_files = [os.path.basename(src.get("source", "Unknown")) for src in category_sources]
                            unique_files = set(source_files)
                            if len(unique_files) <= 2:
                                files_str = ", ".join(unique_files)
                                md_file.write(f"  - {category} ({content_types_str}): {files_str}\n")
                            else:
                                md_file.write(f"  - {category} ({content_types_str}): {len(unique_files)} files\n")
                    
                    # Write resume sources if any, without showing details
                    if resume_sources:
                        md_file.write("- Personal information (resume)\n")
                
                # Flush to ensure content is written to disk
                md_file.flush()
            
            # Optionally display sources
            if show_sources:
                display_sources(formatted_response["sources"])
            
            # Autosave individual response if enabled
            if autosave:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}.md"
                filepath = os.path.join("./chat_logs", filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# Earnable Coach Response\n\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"## You\n\n{query}\n\n")
                    f.write(f"## Coach\n\n{formatted_response['answer'].strip()}\n\n")
                    
                    # Always save sources in autosave mode
                    if formatted_response["sources"]:
                        f.write("## Sources\n\n")
                        
                        # Group and format sources
                        course_sources = []
                        resume_sources = []
                        client_sources = {}
                        
                        for source in formatted_response["sources"]:
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
                        
                        # Write course content sources
                        for idx, source in enumerate(course_sources[:5]):  # Show more sources in autosave
                            module = source.get("module", "Unknown")
                            source_file = os.path.basename(source.get("source", "Unknown"))
                            f.write(f"- **{module}**: {source_file}\n")
                        
                        if len(course_sources) > 5:
                            f.write(f"- *Plus {len(course_sources) - 5} more course content sources*\n")
                        
                        # Write client document sources
                        for client_name, sources in client_sources.items():
                            category_grouped = {}
                            for source in sources:
                                category = source.get("document_category", "general")
                                if category not in category_grouped:
                                    category_grouped[category] = []
                                category_grouped[category].append(source)
                            
                            f.write(f"- **Client ({client_name}) information:**\n")
                            for category, category_sources in category_grouped.items():
                                all_content_types = set()
                                for src in category_sources:
                                    content_types_str = src.get("content_types", "general")
                                    for content_type in [ct.strip() for ct in content_types_str.split(",")]:
                                        all_content_types.add(content_type)
                                
                                content_types_str = ", ".join(sorted(all_content_types))
                                source_files = [os.path.basename(src.get("source", "Unknown")) for src in category_sources]
                                unique_files = set(source_files)
                                if len(unique_files) <= 2:
                                    files_str = ", ".join(unique_files)
                                    f.write(f"  - {category} ({content_types_str}): {files_str}\n")
                                else:
                                    f.write(f"  - {category} ({content_types_str}): {len(unique_files)} files\n")
                        
                        # Write resume sources if any
                        if resume_sources:
                            f.write("- **Personal information** (resume)\n")
                
                console.print(f"[dim]Response saved to {filepath}[/dim]")
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            
            # Save error to file if enabled
            if md_file:
                md_file.write(f"\n### Error\n\n```\n{e}\n```\n")
                md_file.flush()
            
            # Save error in autosave mode too
            if autosave:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_error.md"
                filepath = os.path.join("./chat_logs", filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# Earnable Coach Error\n\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"## You\n\n{query}\n\n")
                    f.write(f"## Error\n\n```\n{e}\n```\n")
                
                console.print(f"[dim]Error saved to {filepath}[/dim]")

@app.command()
def autosave(
    model_name: str = typer.Option("gpt-4", help="Name of the OpenAI model to use"),
    vector_store_path: str = typer.Option("./chroma_db", help="Path to the vector store"),
    profile_path: str = typer.Option("./user_profile.json", help="Path to user profile JSON file"),
    log_dir: str = typer.Option("./chat_logs", help="Directory to save chat logs"),
):
    """
    Start a chat session where every response is automatically saved as a markdown file in a designated directory.
    """
    from datetime import datetime
    import os

    # Load environment variables
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY environment variable is not set.")
        return
    if not os.path.exists(vector_store_path):
        console.print(f"[bold red]Error:[/bold red] Vector store not found at {vector_store_path}")
        return
    try:
        vector_store = load_vector_store(vector_store_path)
    except Exception as e:
        console.print(f"[bold red]Error loading vector store:[/bold red] {e}")
        return
    user_profile = UserProfile(profile_path=profile_path)
    rag_chain = create_rag_chain(vector_store, model_name, use_context_aware_prompting)

    # Initialize greeting generator
    greeting_generator = GreetingGenerator(chat_logs_dir=log_dir, user_profile=user_profile)
    
    # Generate personalized greeting
    greeting_message = greeting_generator.generate_greeting()
    quick_suggestions = greeting_generator.get_quick_start_suggestions()

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Display personalized welcome message
    welcome_panel = f"[bold]Autosave Chat Mode[/bold]\n\n{greeting_message}\n"
    
    if quick_suggestions:
        welcome_panel += "\n[bold]Quick start suggestions:[/bold]\n"
        welcome_panel += "\n".join(quick_suggestions)
        welcome_panel += "\n"
    
    welcome_panel += "\nEvery response will be saved as a markdown file in 'chat_logs'.\nType 'exit' or 'quit' to end."

    console.print(Panel.fit(
        welcome_panel,
        box=ROUNDED,
        border_style="blue",
        padding=(1, 2),
        title="Earnable Coach Autosave"
    ))

    while True:
        query = console.input("\n[bold blue]You:[/bold blue] ")
        if query.lower() in ("exit", "quit"):
            console.print("[bold green]Coach:[/bold green] It was great talking with you. Keep building your business! Goodbye!")
            break
        if not query.strip():
            continue
        try:
            with console.status("[bold]Thinking...[/bold]", spinner="dots"):
                profile_context = user_profile.get_formatted_profile()
                enhanced_query = f"{query}\n\n[User Profile Information: {profile_context}]"
                response = rag_chain.invoke({"question": enhanced_query})
                formatted_response = format_response(response)
                user_profile.extract_info_from_message(query, formatted_response["answer"])
            # Display response
            console.print("\n[bold green]Coach:[/bold green]")
            md = Markdown(formatted_response["answer"].strip())
            console.print(md)
            # Show sources in terminal
            if formatted_response["sources"]:
                display_sources(formatted_response["sources"])
            # Save response to markdown file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}.md"
            filepath = os.path.join(log_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"### Earnable Coach Response\n\n")
                f.write(f"### You\n\n{query}\n\n")
                f.write(f"### Coach\n\n{formatted_response['answer'].strip()}\n\n")
                # Save sources in markdown file
                if formatted_response["sources"]:
                    f.write("### Sources\n\n")
                    # Group and format sources as in chat command
                    course_sources = []
                    resume_sources = []
                    client_sources = {}
                    for source in formatted_response["sources"]:
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
                    # Write course content sources
                    for idx, source in enumerate(course_sources[:3]):
                        module = source.get("module", "Unknown")
                        source_file = os.path.basename(source.get("source", "Unknown"))
                        f.write(f"- {module}: {source_file}\n")
                    if len(course_sources) > 3:
                        f.write(f"- Plus {len(course_sources) - 3} more course content sources\n")
                    # Write client document sources
                    for client_name, sources in client_sources.items():
                        category_grouped = {}
                        for source in sources:
                            category = source.get("document_category", "general")
                            if category not in category_grouped:
                                category_grouped[category] = []
                            category_grouped[category].append(source)
                        f.write(f"- Client ({client_name}) information:\n")
                        for category, category_sources in category_grouped.items():
                            all_content_types = set()
                            for src in category_sources:
                                content_types_str = src.get("content_types", "general")
                                for content_type in [ct.strip() for ct in content_types_str.split(",")]:
                                    all_content_types.add(content_type)
                            content_types_str = ", ".join(sorted(all_content_types))
                            source_files = [os.path.basename(src.get("source", "Unknown")) for src in category_sources]
                            unique_files = set(source_files)
                            if len(unique_files) <= 2:
                                files_str = ", ".join(unique_files)
                                f.write(f"  - {category} ({content_types_str}): {files_str}\n")
                            else:
                                f.write(f"  - {category} ({content_types_str}): {len(unique_files)} files\n")
                    # Write resume sources if any
                    if resume_sources:
                        f.write("- Personal information (resume)\n")
            console.print(f"[dim]Response saved to {filepath}[/dim]")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app() 