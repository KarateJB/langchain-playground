from langchain.agents import create_agent


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


agent = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[get_weather, translate_to_traditional_chinese],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
)

print(result["messages"][-1].content_blocks)
