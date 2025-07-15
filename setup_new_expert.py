#!/usr/bin/env python3
"""
Setup New Expert Script

This script helps users create a new expert configuration for the
sophisticated RAG framework. It guides through the configuration process
and validates the setup.
"""

import os
import sys
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, List
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

app = typer.Typer()
console = Console()

def load_template_config() -> Dict[str, Any]:
    """Load the template configuration"""
    template_path = Path("config/expert_config.yaml")
    if not template_path.exists():
        console.print(f"[red]Template configuration not found at {template_path}[/red]")
        raise typer.Exit(1)
    
    with open(template_path, 'r') as f:
        return yaml.safe_load(f)

def get_expert_profile() -> Dict[str, Any]:
    """Collect expert profile information from user"""
    console.print(Panel.fit("Expert Profile Setup", style="bold blue"))
    
    name = Prompt.ask("Expert's full name")
    teaching_style = Prompt.ask("Teaching style (e.g., 'Direct, systematic, framework-driven')")
    expertise_domain = Prompt.ask("Expertise domain (e.g., 'Business Development', 'Personal Finance')")
    signature_approach = Prompt.ask("Signature approach/methodology")
    
    return {
        "name": name,
        "teaching_style": teaching_style,
        "expertise_domain": expertise_domain,
        "signature_approach": signature_approach
    }

def get_content_types() -> Dict[str, Any]:
    """Configure content types for the expert"""
    console.print(Panel.fit("Content Types Configuration", style="bold blue"))
    
    content_types = {}
    
    # Default content types with explanations
    default_types = {
        "framework": "Systematic approaches and methodologies",
        "mindset": "Psychology and mental model content", 
        "tactical": "Step-by-step actionable guidance",
        "contrarian": "Challenges conventional wisdom",
        "case_study": "Real examples and student stories",
        "testing": "Validation and experimentation content",
        "story": "Narrative and storytelling content",
        "numbers": "Data, metrics, and quantitative content"
    }
    
    console.print("Configure content types for your expert:")
    for content_type, description in default_types.items():
        include = Confirm.ask(f"Include '{content_type}' ({description})?", default=True)
        if include:
            weight = float(Prompt.ask(f"Weight for '{content_type}' (0.1-1.0)", default="0.8"))
            content_types[content_type] = {
                "description": description,
                "weight": weight
            }
    
    # Allow custom content types
    while Confirm.ask("Add custom content type?", default=False):
        name = Prompt.ask("Content type name")
        description = Prompt.ask("Description")
        weight = float(Prompt.ask("Weight (0.1-1.0)", default="0.8"))
        content_types[name] = {
            "description": description,
            "weight": weight
        }
    
    return content_types

def get_signature_phrases(expert_name: str) -> Dict[str, Any]:
    """Configure signature phrases for the expert"""
    console.print(Panel.fit("Signature Phrases Configuration", style="bold blue"))
    
    signature_phrases = {
        "framework_indicators": [],
        "mindset_indicators": [],
        "tactical_indicators": [],
        "contrarian_indicators": [],
        "case_study_indicators": []
    }
    
    categories = {
        "framework_indicators": "Framework and systems language",
        "mindset_indicators": "Mindset and psychology phrases",
        "tactical_indicators": "Tactical execution phrases", 
        "contrarian_indicators": "Contrarian indicators",
        "case_study_indicators": "Case study patterns"
    }
    
    for category, description in categories.items():
        console.print(f"\\n[bold]{description}[/bold]")
        phrases = []
        
        while True:
            phrase = Prompt.ask(f"Add phrase for {category} (or press Enter to finish)", default="")
            if not phrase:
                break
                
            content_type = Prompt.ask("Content type this indicates", default="framework")
            weight = float(Prompt.ask("Weight (0.1-1.0)", default="0.8"))
            
            phrases.append({
                "phrase": phrase,
                "content_type": content_type,
                "weight": weight
            })
        
        signature_phrases[category] = phrases
    
    return signature_phrases

def get_frameworks() -> Dict[str, Any]:
    """Configure expert frameworks"""
    console.print(Panel.fit("Frameworks Configuration", style="bold blue"))
    
    frameworks = {}
    
    while Confirm.ask("Add a framework?", default=True):
        name = Prompt.ask("Framework name")
        description = Prompt.ask("Framework description")
        
        keywords = []
        console.print("Add keywords for this framework:")
        while True:
            keyword = Prompt.ask("Keyword (or press Enter to finish)", default="")
            if not keyword:
                break
            keywords.append(keyword)
        
        frameworks[name] = {
            "keywords": keywords,
            "description": description
        }
        
        if len(frameworks) >= 3 and not Confirm.ask("Add another framework?", default=False):
            break
    
    return frameworks

def get_voice_patterns(expert_name: str) -> Dict[str, List[str]]:
    """Configure voice patterns for the expert"""
    console.print(Panel.fit("Voice Patterns Configuration", style="bold blue"))
    
    voice_patterns = {}
    
    pattern_types = {
        "contrarian_openers": f"How {expert_name} challenges conventional thinking",
        "framework_introductions": f"How {expert_name} introduces frameworks",
        "tactical_language": f"How {expert_name} gives tactical advice",
        "mindset_shifts": f"How {expert_name} addresses psychology", 
        "case_study_setups": f"How {expert_name} introduces examples"
    }
    
    for pattern_type, description in pattern_types.items():
        console.print(f"\\n[bold]{description}[/bold]")
        patterns = []
        
        # Provide some default examples
        if pattern_type == "contrarian_openers":
            patterns.append(f"Here's where most people get this wrong:")
        elif pattern_type == "framework_introductions":
            patterns.append(f"Here's the exact framework I use:")
        elif pattern_type == "tactical_language":
            patterns.append(f"Here's exactly what to do:")
        
        while True:
            pattern = Prompt.ask(f"Add pattern for {pattern_type} (or press Enter to finish)", default="")
            if not pattern:
                break
            patterns.append(pattern)
        
        voice_patterns[pattern_type] = patterns
    
    return voice_patterns

def get_signature_phrases_by_context() -> Dict[str, str]:
    """Configure signature phrases for different contexts"""
    console.print(Panel.fit("Context-Specific Signatures", style="bold blue"))
    
    contexts = [
        "first_sale", "customer_research", "pricing", "offers",
        "mindset", "frameworks", "tactical", "general"
    ]
    
    signatures = {}
    general_signature = Prompt.ask("General signature phrase", default="Focus on the fundamentals.")
    
    for context in contexts:
        if context == "general":
            signatures[context] = general_signature
        else:
            signature = Prompt.ask(f"Signature for '{context}' context", default=general_signature)
            signatures[context] = signature
    
    return signatures

def create_expert_config(expert_name: str) -> Dict[str, Any]:
    """Create a complete expert configuration"""
    config = load_template_config()
    
    # Update expert profile
    config["expert_profile"] = get_expert_profile()
    
    # Update content types
    config["content_types"] = get_content_types()
    
    # Update signature phrases
    config["signature_phrases"] = get_signature_phrases(expert_name)
    
    # Update frameworks
    config["frameworks"] = get_frameworks()
    
    # Update voice patterns
    config["voice_patterns"] = get_voice_patterns(expert_name)
    
    # Update signature phrases by context
    config["signature_phrases_by_context"] = get_signature_phrases_by_context()
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate the expert configuration"""
    console.print(Panel.fit("Validating Configuration", style="bold blue"))
    
    required_sections = [
        "expert_profile", "content_types", "signature_phrases",
        "frameworks", "voice_patterns", "signature_phrases_by_context"
    ]
    
    for section in required_sections:
        if section not in config:
            console.print(f"[red]Missing required section: {section}[/red]")
            return False
    
    # Validate expert profile
    profile = config["expert_profile"]
    required_profile_fields = ["name", "teaching_style", "expertise_domain", "signature_approach"]
    for field in required_profile_fields:
        if not profile.get(field):
            console.print(f"[red]Missing expert profile field: {field}[/red]")
            return False
    
    console.print("[green]Configuration validation passed![/green]")
    return True

def save_config(config: Dict[str, Any], output_path: Path):
    """Save the configuration to a file"""
    os.makedirs(output_path.parent, exist_ok=True)
    
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    console.print(f"[green]Configuration saved to {output_path}[/green]")

def display_next_steps(config_path: Path, expert_name: str):
    """Display next steps for the user"""
    steps = f"""
# Next Steps

1. **Review Configuration**: Check {config_path} and make any necessary adjustments

2. **Set Environment Variable**: 
   ```bash
   export EXPERT_CONFIG_PATH="{config_path}"
   ```

3. **Index Documents**: Place your expert's content in a directory and run:
   ```bash
   python src/index_documents.py
   ```

4. **Test the System**: Start a chat session:
   ```bash
   python src/chat.py chat
   ```

5. **Customize Further**: Edit {config_path} to fine-tune:
   - Document type patterns
   - Authority level indicators
   - Retrieval priorities
   - Query intent classification

Your sophisticated RAG framework for {expert_name} is now ready!
"""
    
    console.print(Panel(Markdown(steps), title="Setup Complete!", style="bold green"))

@app.command()
def setup(
    expert_name: str = typer.Argument(..., help="Name of the expert (for config filename)"),
    output_dir: str = typer.Option("config/experts", help="Output directory for config file"),
    interactive: bool = typer.Option(True, help="Interactive setup mode")
):
    """
    Set up a new expert configuration for the sophisticated RAG framework.
    """
    console.print(Panel.fit(f"Setting up configuration for {expert_name}", style="bold blue"))
    
    if not interactive:
        console.print("[red]Non-interactive mode not yet implemented[/red]")
        raise typer.Exit(1)
    
    try:
        # Create expert configuration
        config = create_expert_config(expert_name)
        
        # Validate configuration
        if not validate_config(config):
            console.print("[red]Configuration validation failed[/red]")
            raise typer.Exit(1)
        
        # Save configuration
        config_filename = f"{expert_name.lower().replace(' ', '_')}_config.yaml"
        config_path = Path(output_dir) / config_filename
        save_config(config, config_path)
        
        # Display next steps
        display_next_steps(config_path, expert_name)
        
    except KeyboardInterrupt:
        console.print("\\n[yellow]Setup cancelled by user[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"[red]Error during setup: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def validate(config_path: str = typer.Argument(..., help="Path to expert config file")):
    """
    Validate an expert configuration file.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        console.print(f"[red]Configuration file not found: {config_path}[/red]")
        raise typer.Exit(1)
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        if validate_config(config):
            console.print(f"[green]Configuration at {config_path} is valid![/green]")
        else:
            console.print(f"[red]Configuration at {config_path} has errors[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]Error validating configuration: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def list_configs(config_dir: str = typer.Option("config", help="Configuration directory")):
    """
    List available expert configurations.
    """
    config_path = Path(config_dir)
    
    if not config_path.exists():
        console.print(f"[red]Configuration directory not found: {config_dir}[/red]")
        raise typer.Exit(1)
    
    # Find all YAML config files
    config_files = list(config_path.rglob("*_config.yaml"))
    template_files = list(config_path.rglob("expert_config.yaml"))
    
    if not config_files and not template_files:
        console.print("[yellow]No expert configurations found[/yellow]")
        return
    
    table = Table(title="Available Expert Configurations")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Type", style="yellow")
    
    # Add template files
    for template_file in template_files:
        table.add_row(
            "Template",
            str(template_file),
            "Template"
        )
    
    # Add expert-specific configs
    for config_file in config_files:
        expert_name = config_file.stem.replace("_config", "").replace("_", " ").title()
        table.add_row(
            expert_name,
            str(config_file),
            "Expert Config"
        )
    
    console.print(table)

if __name__ == "__main__":
    app()