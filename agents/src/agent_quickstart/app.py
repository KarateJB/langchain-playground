import json
import sys
import urllib.error
import urllib.request

from deepagents import create_deep_agent
from langchain.agents import create_agent
from langchain.tools import tool
# from langgraph.checkpoint.memory import InMemorySaver

# checkpointer = InMemorySaver()

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def translate_to_traditional_chinese(text: str) -> str:
    """Translate text into traditional Chinese."""
    # Simple demo translations
    translations = {
        "hello": "你好",
        "goodbye": "再見",
        "thank you": "謝謝",
        "good morning": "早上好",
    }
    return translations.get(text.lower(), f"[Traditional Chinese: {text}]")

@tool
def fetch_text_from_url(url: str) -> str:
    """Fetch the document from a URL.
    """
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
1. get_weather - Get weather information for a given city. Example: "Get weather in Paris"
2. translate_to_traditional_chinese - Translate text to Traditional Chinese. Example: "Translate 'hello' to Traditional Chinese"
3. fetch_text_from_url - Fetch the text content from a given URL. Example: "Fetch text from 'https://example.com'"
4. list_tools - Display this help message listing all available tools.
    """.strip()
    return tools_info


def ask_agent(question: str):
    """Ask the agent a question and print the response."""
    # agent = create_agent(
    #     model="google_genai:gemini-3.5-flash-lite",
    #     tools=[get_weather, translate_to_traditional_chinese, list_tools],
    #     system_prompt="You are a helpful assistant",
    # )
    agent = create_deep_agent(
        model="google_genai:gemini-3.5-flash-lite",
        tools=[get_weather, translate_to_traditional_chinese, fetch_text_from_url, list_tools],
        system_prompt="You are a helpful assistant",
        # checkpointer=checkpointer
    )

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    # Format output as proper JSON with double quotes
    print(json.dumps(result["messages"][-1].content_blocks, indent=2, ensure_ascii=False))

def main():
    # Get question from command line or use default
    if len(sys.argv) > 1 and " ".join(sys.argv[1:]).strip():
        question = " ".join(sys.argv[1:])
    else:
        question = "Please greet me and tell me what tools are available. Use the list_tools function to show what I can do."

    ask_agent(question)

if __name__ == "__main__":
    main()
