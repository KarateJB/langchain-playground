
# LangChain Agents

A LangChain-based agent that uses Google's Gemini model to understand user questions and intelligently use available tools to provide answers.

## Overview

This project demonstrates how LangChain agents work by creating an interactive agent with multiple tools. The agent understands natural language queries and decides which tool to use based on the user's request.

## Prerequisites

- Python 3.11+
- `uv` package manager
- Google API key (set as `GOOGLE_API_KEY` environment variable)

## Setup

1. Install dependencies:

```bash
# 1: Install new packages if not already added
uv add langchain deepagents langchain-google-genai
uv add deepagents

# 2: If already in pyproject.toml, just sync
uv sync
```

2. Set your Google API key:

```bash
export GOOGLE_API_KEY="your-api-key-here"  # On Linux/Mac or Bash
set GOOGLE_API_KEY=your-api-key-here  # On Windows CMD
$env:GOOGLE_API_KEY="your-api-key-here"  # On Windows PowerShell
```

## Available Tools

The agent has access to the following tools:

1. **get_weather(city)** - Get weather information for a given city
   - Example: "What's the weather in Paris?"
   - Returns: A weather description for the specified city

2. **translate_to_traditional_chinese(text)** - Translate text into Traditional Chinese
   - Example: "Translate 'hello' to Traditional Chinese"
   - Supports: hello, goodbye, thank you, good morning (and extensible)

3. **list_tools()** - List all available tools
   - Example: "What tools are available?"
   - Returns: Descriptions of all accessible tools

## Usage

### Default behavior (with greeting and tool listing):

```bash
uv run python -m agent_quickstart.main
```
This triggers the agent to greet you and show all available tools.

### Ask a custom question:

```bash
uv run python -m agent_quickstart.main "What's the weather in San Francisco?"
```

### Get translations:

```bash
uv run python -m agent_quickstart.main "Translate 'thank you' to Traditional Chinese"
```

### View available tools:

```bash
uv run python -m agent_quickstart.main "What tools do I have access to?"
```

## Output Format

The response is formatted as JSON with proper Unicode support for displaying Traditional Chinese characters:

```json
[
  {
    "type": "text",
    "text": "Response from the agent",
    "extras": {
      "signature": "..."
    }
  }
]
```

## How It Works

1. User provides a question (via command line or default)
2. LangChain creates an agent with the Gemini 3.5 Flash Lite model
3. The agent analyzes the question and decides which tools to use
4. Tools are executed and results are returned to the agent
5. The agent formats a natural language response
6. Output is printed as formatted JSON

## Example Conversations

```bash
# Weather query
$ uv run python -m agent_quickstart.main "What's the weather in Tokyo?"

# Translation
$ uv run python -m agent_quickstart.main "Say 'good morning' in Traditional Chinese"

# Tool discovery
$ uv run python -m agent_quickstart.main "List all available tools"
```
