"""
Main CLI entry point for Alex Persona AI Chatbot.

Provides Click-based command-line interface for starting the interactive chat.
"""

import asyncio
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from src.cli.chat import run_chat_cli
from src.core.config import config


@click.group()
@click.version_option(version="1.0.0", prog_name="Alex Persona AI Chatbot")
def cli():
    """Alex Persona AI Chatbot - Chat with an AI version of Alex Shulga."""
    pass


@cli.command()
@click.option(
    '--rebuild-rag',
    is_flag=True,
    help='Rebuild the RAG vector store from conversation files'
)
@click.option(
    '--session-id',
    type=str,
    help='Load a specific conversation session'
)
def chat(rebuild_rag: bool, session_id: str):
    """Start an interactive chat session with Alex Persona AI."""
    try:
        # Validate configuration
        config.validate_config()

        click.echo("🤖 Starting Alex Persona AI Chatbot...")

        if rebuild_rag:
            click.echo("🔄 Rebuilding RAG system from conversations...")

        if session_id:
            click.echo(f"📂 Loading session: {session_id}")

        # Run the chat CLI
        asyncio.run(run_chat_cli())

    except ValueError as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        click.echo("\n💡 Please check your .env file and ensure all required variables are set.")
        click.echo("Run 'cp .env.example .env' and edit the .env file with your settings.")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n👋 Chat session interrupted.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def init():
    """Initialize the Alex Persona AI system."""
    try:
        click.echo("🚀 Initializing Alex Persona AI system...")

        # Check if .env exists, if not create from template
        env_file = Path(".env")
        env_example = Path(".env.example")

        if not env_file.exists() and env_example.exists():
            env_file.write_text(env_example.read_text())
            click.echo("📝 Created .env file from template")
            click.echo("⚠️  Please edit .env file with your OpenAI API key and other settings")

        # Create data directories
        from src.core.config import config
        config._create_directories()

        click.echo("📁 Created data directories")
        click.echo("✅ Initialization complete!")
        click.echo("\n📌 Next steps:")
        click.echo("1. Edit .env file with your OpenAI API key")
        click.echo("2. Run 'python cli.py chat' to start chatting")

    except Exception as e:
        click.echo(f"❌ Error during initialization: {e}", err=True)
        sys.exit(1)


@cli.command()
def info():
    """Show system information and configuration."""
    try:
        from src.core.config import config
        from src.core.utils import load_conversation_files

        click.echo("📊 Alex Persona AI System Information")
        click.echo("=" * 40)

        # Configuration info
        click.echo(f"LLM Model: {config.llm_model}")
        click.echo(f"Embedding Model: {config.embedding_model}")
        click.echo(f"Max Conversation History: {config.max_conversation_history}")
        click.echo(f"Vector Store Path: {config.vector_store_path}")
        click.echo(f"Session Store Path: {config.session_store_path}")

        # Conversation data info
        conversation_files = load_conversation_files(config.conversation_data_path)
        click.echo(f"Conversation Files: {len(conversation_files)}")

        for file_path in conversation_files:
            click.echo(f"  - {file_path.name}")

        # Vector store status
        vector_exists = (config.vector_store_path / "index.faiss").exists()
        click.echo(f"Vector Store: {'✅ Ready' if vector_exists else '❌ Not built'}")

        # Session data
        session_files = list(config.session_store_path.glob("*.json"))
        click.echo(f"Saved Sessions: {len(session_files)}")

    except Exception as e:
        click.echo(f"❌ Error getting system info: {e}", err=True)


@cli.command()
@click.option(
    '--days',
    type=int,
    default=30,
    help='Delete sessions older than this many days'
)
def cleanup(days: int):
    """Clean up old conversation sessions."""
    try:
        from src.core.memory import ConversationMemory

        memory = ConversationMemory()
        deleted_count = memory.cleanup_old_sessions(days)

        click.echo(f"🧹 Cleaned up {deleted_count} sessions older than {days} days")

    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}", err=True)


if __name__ == "__main__":
    cli()
