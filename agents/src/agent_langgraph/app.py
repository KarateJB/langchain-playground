import json
import sys
import urllib.error
import urllib.request

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

# Load environment variables from .env file
load_dotenv()

SYSTEM_PROMPT = """
You are a literary data assistant.

## Capabilities

- `fetch_text_from_url`: loads document text from a URL into the conversation.
Do not guess line counts or positions—ground them in tool results from the saved file.
"""

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


def analyze_great_gatsby():
    """Analyze The Great Gatsby from Project Gutenberg with memory persistence."""
    content = f"""Project Gutenberg hosts a full plain-text copy of F. Scott Fitzgerald's The Great Gatsby.
URL: https://www.gutenberg.org/files/64317/64317-0.txt

Answer as much as you can:

1) How many lines in the complete Gutenberg file contain the substring `Gatsby` (count lines, not occurrences within a line, each line ends with a line break).
2) The 1-based line number of the first line in the file that contains `Daisy`.
3) A two-sentence neutral synopsis.

Do your best on (1) and (2). If at any point you realize you cannot **verify** an exact answer with
your available tools and reasoning, do not fabricate numbers: use `null` for that field and spell out
the limitation in `how_you_computed_counts`. If you encounter any errors please report what the error was and what the error message was."""

    manager = AgentManager(use_checkpointer=True)

    # You can choose LangChain agent or Deep agent

    # agent = manager.create_agent()
    # print("Running create_agent...", flush=True)
    # agent_result = agent.invoke(
    #     {"messages": [{"role": "user", "content": content}]},
    #     config={"configurable": {"thread_id": "great-gatsby-lc"}},
    # )

    deep_agent = manager.create_deep_agent()
    print("Running create_deep_agent...", flush=True)
    deep_agent_result = deep_agent.invoke(
        {"messages": [{"role": "user", "content": content}]},
        config={"configurable": {"thread_id": "great-gatsby-da"}},
    )

    # result = agent_result["messages"][-1].content_blocks
    result = deep_agent_result["messages"][-1].content_blocks

    print(json.dumps(result, indent=2, ensure_ascii=False))


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
        if command == "gatsby":
            analyze_great_gatsby()
            return
        # Otherwise treat all arguments as a question
        question = " ".join(sys.argv[1:])
    else:
        question = "Please greet me and tell me what tools are available. Use the list_tools function to show what I can do."

    ask_agent(question)


if __name__ == "__main__":
    main()
