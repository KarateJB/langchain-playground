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


def ask_agent(question: str):

    model = init_chat_model(
        "gemini-3.5-flash-lite",
        model_provider="google-genai",
        temperature=0.5,
        timeout=600,
        max_tokens=25000,
        streaming=True,
    )

    """Ask the agent a question and print the response."""
    # agent = create_agent(
    #     model=model,
    #     tools=[fetch_text_from_url, list_tools],
    #     system_prompt=SYSTEM_PROMPT,
    #     checkpointer=checkpointer,
    # )
    agent = create_deep_agent(
        model=model,
        tools=[fetch_text_from_url, list_tools],
        system_prompt=SYSTEM_PROMPT,
        # checkpointer=checkpointer
    )

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    # Format output as proper JSON with double quotes
    print(
        json.dumps(result["messages"][-1].content_blocks, indent=2, ensure_ascii=False)
    )


def main():
    # Get question from command line or use default
    if len(sys.argv) > 1 and " ".join(sys.argv[1:]).strip():
        question = " ".join(sys.argv[1:])
    else:
        question = "Please greet me and tell me what tools are available. Use the list_tools function to show what I can do."

    ask_agent(question)


if __name__ == "__main__":
    main()
