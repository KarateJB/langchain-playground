# LangChain Playground

A small project for exploring LangChain, LangGraph, and Dockerized AI agent workflows with Google Gemini.

What this project includes:
- LangChain-based agent examples for quick experimentation
- A LangGraph agent with persistent conversation memory
- PostgreSQL-backed thread memory for session continuity
- Docker setup for running the agent and database together locally
- AI news workflow that can generate and save curated summaries

---
## Main features

### Agent examples

The project includes multiple agent patterns for learning and testing how LLM tools, prompts, and orchestration work.

### LangGraph memory

The LangGraph app stores conversational state in PostgreSQL, keyed by a thread ID so the same session can be resumed across runs.

### Dockerized local environment

The repository includes containerized setup for:

- the Python agent application
- a PostgreSQL database
- local startup and service orchestration

### Practical AI workflows

It also includes a demo workflow for collecting and summarizing AI-related content, showing how agents can work with external data and save outputs.

---
## Quick start

For implementation details and commands, see:

- [agents/README.md](agents/README.md)
- [docker/README.md](docker/README.md)
