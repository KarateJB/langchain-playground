import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from langgraph.checkpoint.memory import InMemorySaver
from .output_utils import content_blocks_to_markdown, save_to_markdown_file

checkpointer = InMemorySaver()

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


class AgentManager:
    """Manages agent and model initialization."""

    def __init__(self, use_checkpointer: bool = False):
        """Initialize AgentManager.
        
        Args:
            use_checkpointer: Whether to use memory checkpointer for agent.
        """
        self.model = init_chat_model(**MODEL_CONFIG)
        self.use_checkpointer = use_checkpointer

    def create_agent(self):
        """Create a standard LangChain agent."""
        kwargs = {
            "model": self.model,
            "tools": TOOLS,
            "system_prompt": SYSTEM_PROMPT,
        }
        if self.use_checkpointer:
            kwargs["checkpointer"] = checkpointer
        return create_agent(**kwargs)

    def create_deep_agent(self):
        """Create a DeepAgents agent."""
        kwargs = {
            "model": self.model,
            "tools": TOOLS,
            "system_prompt": SYSTEM_PROMPT,
        }
        if self.use_checkpointer:
            kwargs["checkpointer"] = checkpointer
        return create_deep_agent(**kwargs)

def collect_ai_news():
    """Analyze the latest AI news with memory persistence."""
    try:
        content = load_content("collect-ai-news.txt")
    except FileNotFoundError:
        return
    
    manager = AgentManager(use_checkpointer=True)
    deep_agent = manager.create_deep_agent()
    
    print("Running collect_ai_news...", flush=True)
    deep_agent_result = deep_agent.invoke(
        {"messages": [{"role": "user", "content": content}]},
        config={"configurable": {"thread_id": "ai-news"}},
    )

    result = deep_agent_result["messages"][-1].content_blocks
    
    # Convert to markdown format
    markdown_content = content_blocks_to_markdown(result)
    
    # Save to file with today's date
    filepath = save_to_markdown_file(markdown_content)
    
    print(f"Output saved to: {filepath}")

def ask_agent(question: str):
    """Ask the agent a question and print the response."""
    manager = AgentManager(use_checkpointer=False)
    agent = manager.create_deep_agent()

    agent_result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    result = agent_result["messages"][-1].content_blocks

    # Format output as proper JSON with double quotes
    print(
        json.dumps(result, indent=2, ensure_ascii=False)
    )


def main():
    # Get command from command line
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        match command:
            case "ainews":
                collect_ai_news()
                return
            # case "example": # Add other command and callback function if needed
            #     example()
            #     return
            case _:
                # Otherwise treat all arguments as a question
                question = " ".join(sys.argv[1:])
    else:
        question = "Please greet me and tell me what tools are available. Use the list_tools function to show what I can do."

    ask_agent(question)


if __name__ == "__main__":
    main()
