
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
## For agent_quickstart and agent_langgraph
uv add langchain deepagents langchain-google-genai python-dotenv
## Additional packages for agent_langgraph
uv add langgraph-checkpoint-postgres "psycopg[binary]"

# 2: If already in pyproject.toml, just sync
uv sync
```

2. Set your environment variables

The environment variables include:

- Google API key
- PostgreSQL connection string (required for LangGraph)
- LangSmith (optional)

See "agents/.env.sample" and create "agents/.env" file with the same environment variables. 
Or you can set them in your command line, e.g., to set the `GOOGLE_API_KEY`:

```bash
export GOOGLE_API_KEY="your-api-key-here"  # On Linux/Mac or Bash
set GOOGLE_API_KEY=your-api-key-here  # On Windows CMD
$env:GOOGLE_API_KEY="your-api-key-here"  # On Windows PowerShell
```

---
## Available Tools

The program provides the following agents:
- **Agent Quickstart**: A simple agent that can answer questions by LangChain agent or Deep Agent. The source files are located in `agents/agent_quickstart`.
- **LangGraph Agent**: A more advanced agent that can use LangGraph to store and retrieve information. The source files are located in `agents/agent_langgraph`.

### Agent Quickstart

The LangChain agent has access to the following tools:

1. `get_weather(city)` - Get weather information for a given city.
2. `translate_to_traditional_chinese(text)` - Translate text into Traditional Chinese.
3. `fetch_text_from_url(url)` - Fetch the text content from a given URL.
4. `list_tools()` - List all available tools.


### LangGraph Agent

The LangGraph agent supports:

1. `fetch_text_from_url(url)` - Fetches the content of a web page and returns the text.
2. `list_tools()` - Lists the tools available to the agent.
3. Persistent memory using `langgraph.checkpoint.postgres.PostgresSaver`.
4. Thread-based conversation continuity keyed by a `thread_id`.

The agent runs with Google Gemini and stores conversation checkpoints in PostgreSQL so the same session can continue across runs.

---
## Usage

Run the agents from the `agents/` directory.

### Agent Quickstart

#### Default behavior (greeting)

```bash
uv run greeting
```

#### Greeting and tool listing

```bash
uv run python -m agent_quickstart.app
```
This triggers the agent to greet you and show all available tools.

#### Ask a custom question:

Use `uv run python -m agent_quickstart.app` or `uv run agent-quickstart` followed by your question to interact with the agent.  

Example:
```bash
# Ask about weather
uv run python -m agent_quickstart.app "What's the weather in San Francisco?"
# Translation
uv run python -m agent_quickstart.app "Translate 'thank you' to Traditional Chinese"
# Fetch text from URL
uv run agent-quickstart "Please read 'https://www.theprp.com/2026/09/19/news/marc-hudson-steps-back-from-dragonforce-am
id-tinnitus-issues-replacement-announced/' and give me a summary in Traditional Chinese"
```

Or view available tools without asking a specific question:
```bash
uv run agent-quickstart
```

### LangGraph Agent

```bash
uv run agent-langgraph --help|-h
```

#### Basic usage

```bash
# Default greeting when no question is provided
uv run agent-langgraph

# Ask a question in the default thread
uv run agent-langgraph "Please greet me and list the tools you can use."

# Use a named thread to keep the same conversation memory across runs
uv run agent-langgraph --thread customer-support "Can you summarize the page at https://example.com?"
```

#### Reuse the same session memory

The agent stores checkpoints in PostgreSQL using the `thread_id` value. If you use the same thread ID again, the agent can continue the same conversation.

```bash
uv run agent-langgraph --thread my-session "I am planning a product launch and want to review the latest AI news."
uv run agent-langgraph --thread my-session "Now give me a short action plan based on the previous discussion."
```

The default thread ID is "default" if the argument `--thread` is skipped.

#### Run the built-in AI news workflow

```bash
uv run agent-langgraph --thread ai-news ainews
```

- This loads the AI news content and saves a generated summary to a markdown output file while preserving session state for the same thread.
- The initial prompt is from "agents/src/agent_langgraph/contents/collect-ai-news.txt"


---
## How It Works

### Agent (Quickstart)

1. User provides a question (via command line or default)
2. LangChain creates an agent with the Gemini 3.5 Flash Lite model
3. The agent analyzes the question and decides which tools to use
4. Tools are executed and results are returned to the agent
5. The agent formats a natural language response
6. Output is printed as formatted JSON

### LangGraph Agent

1. The app loads environment settings from `.env` and falls back to default PostgreSQL values.
2. It opens a `PostgresSaver` connection and calls `checkpointer.setup()` so the required checkpoint tables exist.
3. The `AgentManager` creates a Deep Agent with a `checkpointer` when `use_checkpointer=True`.
4. Each conversation is associated with a `thread_id`.
5. When the same `thread_id` is used again, LangGraph loads the previous checkpoint state and the agent can continue the conversation naturally.
6. The final response is returned as JSON content blocks, which are shown in the terminal.

This makes the agent stateful while keeping the memory in PostgreSQL rather than only in memory.

---
## Example Conversations

Agent quickstart:
```bash
# Weather query
$ uv run python -m agent_quickstart.main "What's the weather in Tokyo?"

# Translation
$ uv run python -m agent_quickstart.main "Say 'good morning' in Traditional Chinese"

# Tool discovery
$ uv run python -m agent_quickstart.main "List all available tools"
```

LangGraph agent:
```bash
# Start a new thread and ask a question
$ uv run agent-langgraph --thread research "Summarize this article: https://example.com"

# Continue the same conversation later
$ uv run agent-langgraph --thread research "Now turn that summary into bullet points for a presentation."

# Use the default thread
$ uv run agent-langgraph "What tools are available?"

# Generate the AI news summary and keep it in the same thread
$ uv run agent-langgraph --thread ai-news ainews
```

