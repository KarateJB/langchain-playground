import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from agent_checkpointers import configured_checkpointer

from .output_utils import (
    content_blocks_to_markdown,
    configure_utf8_streams,
    save_to_markdown_file,
)

# Load environment variables from .env file
load_dotenv()


def load_system_prompt() -> str:
    """Load system prompt from markdown file."""
    prompt_file = Path(__file__).parent / "prompt.md"
    return prompt_file.read_text(encoding="utf-8").strip()


def load_content(filename: str) -> str:
    """Load content from a text file in the contents folder.

    Args:
        filename: Name of the file to load (e.g., "analyze_great_gatsby.txt")

    Returns:
        Content as string

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    content_file = Path(__file__).parent / "contents" / filename

    if not content_file.exists():
        error_msg = f"Error: Content file not found: {content_file}"
        print(error_msg, file=sys.stderr)
        raise FileNotFoundError(error_msg)

    try:
        return content_file.read_text(encoding="utf-8").strip()
    except Exception as e:
        error_msg = f"Error reading content file {filename}: {e}"
        print(error_msg, file=sys.stderr)
        raise


SYSTEM_PROMPT = load_system_prompt()

MODEL_CONFIG = {
    "model": "gemini-3.5-flash-lite",
    "model_provider": "google-genai",
    # "temperature": 0.5, # Set temperature only if the model supports it
    "timeout": 600,
    "max_tokens": 25000,
}


@tool
def fetch_text_from_url(url: str) -> str:
    """Fetch the document from a URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; quickstart-research/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"
    text = raw.decode("utf-8", errors="replace")
    return text


@tool
def list_tools() -> str:
    """List and describe all available tools."""
    tools_info = """
Available Tools:
1. fetch_text_from_url - Fetch the text content from a given URL. Example: "Fetch text from 'https://example.com'"
2. list_tools - Display this help message listing all available tools.
    """.strip()
    return tools_info


TOOLS = [fetch_text_from_url, list_tools]


def invoke_agent(agent, question: str, thread_id: str) -> list:
    """Invoke an agent and turn runtime errors into a text content block."""
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"configurable": {"thread_id": thread_id}},
        )
    except Exception as error:  # noqa: BLE001
        print(error, flush=True)
        return [
            {
                "type": "text",
                "text": "The agent cannot respond now. Please try again later.",
            }
        ]

    return result["messages"][-1].content_blocks


class AgentManager:
    """Manages agent and model initialization."""

    def __init__(self, use_checkpointer: bool = False, checkpointer=None):
        """Initialize AgentManager, optionally using a LangGraph checkpointer."""
        self.model = init_chat_model(**MODEL_CONFIG)
        if use_checkpointer and checkpointer is None:
            raise ValueError("A checkpointer is required when use_checkpointer is True.")
        self.use_checkpointer = use_checkpointer
        self.checkpointer = checkpointer

    def create_agent(self):
        """Create a standard LangChain agent."""
        kwargs = {
            "model": self.model,
            "tools": TOOLS,
            "system_prompt": SYSTEM_PROMPT,
        }
        if self.use_checkpointer:
            kwargs["checkpointer"] = self.checkpointer
        return create_agent(**kwargs)

    def create_deep_agent(self):
        """Create a DeepAgents agent."""
        kwargs = {
            "model": self.model,
            "tools": TOOLS,
            "system_prompt": SYSTEM_PROMPT,
        }
        if self.use_checkpointer:
            kwargs["checkpointer"] = self.checkpointer
        return create_deep_agent(**kwargs)

def collect_ai_news(thread_id: str | None = None):
    """Analyze the latest AI news with memory persistence."""
    thread_id = thread_id or os.getenv("AGENT_SESSION_ID", "ai-news")
    try:
        content = load_content("collect-ai-news.txt")
    except FileNotFoundError:
        return

    with configured_checkpointer() as checkpointer:
        manager = AgentManager(use_checkpointer=True, checkpointer=checkpointer)
        deep_agent = manager.create_deep_agent()

        print("Running collect_ai_news...", flush=True)
        result = invoke_agent(deep_agent, content, thread_id)

    # Convert to markdown format
    markdown_content = content_blocks_to_markdown(result)
    
    # Save to file with today's date
    filepath = save_to_markdown_file(markdown_content)
    
    print(
        json.dumps(
            [{"type": "text", "text": f"AI news output saved to: {filepath}"}],
            indent=2,
            ensure_ascii=False,
        )
    )

def ask_agent(question: str, thread_id: str | None = None):
    """Ask the agent a question and print the response."""

    thread_id = thread_id or os.getenv("AGENT_SESSION_ID", "default")
    with configured_checkpointer() as checkpointer:
        manager = AgentManager(use_checkpointer=True, checkpointer=checkpointer)
        agent = manager.create_deep_agent()

        result = invoke_agent(agent, question, thread_id)

    # Format output as proper JSON with double quotes
    print(
        json.dumps(result, indent=2, ensure_ascii=False)
    )


def main():
    configure_utf8_streams()
    parser = argparse.ArgumentParser(description="Run the LangGraph agent.")
    parser.add_argument(
        "--thread",
        dest="thread_id",
        help="Thread ID to use for loading and saving conversation memory.",
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="Question to ask, or 'ainews' to collect AI news.",
    )
    args = parser.parse_args()
    question = " ".join(args.question).strip()

    if not question:
        question = "Please greet me and tell me what tools are available. Use the list_tools function to show what I can do."

    if question.lower() == "ainews":
        collect_ai_news(thread_id=args.thread_id)
        return

    ask_agent(question, thread_id=args.thread_id)


if __name__ == "__main__":
    main()
