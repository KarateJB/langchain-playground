from langchain.agents import create_agent
import sys
import json


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


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


def list_tools() -> str:
    """List and describe all available tools."""
    tools_info = """
Available Tools:
1. get_weather(city: str) - Get weather information for a given city. Example: "Get weather in Paris"
2. translate_to_traditional_chinese(text: str) - Translate text to Traditional Chinese. Example: "Translate 'hello' to Traditional Chinese"
3. list_tools() - Display this help message listing all available tools.

You can ask me to use any of these tools!
    """.strip()
    return tools_info


def ask_agent(question: str):
    """Ask the agent a question and print the response."""
    agent = create_agent(
        model="google_genai:gemini-3.5-flash-lite",
        tools=[get_weather, translate_to_traditional_chinese, list_tools],
        system_prompt="You are a helpful assistant",
    )
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    
    # Format output as proper JSON with double quotes
    print(json.dumps(result["messages"][-1].content_blocks, indent=2))


if __name__ == "__main__":
    # Get question from command line or use default
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "Please greet me and tell me what tools are available. Use the list_tools function to show what I can do."
    
    ask_agent(question)
