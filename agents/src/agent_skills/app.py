import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from agent_checkpointers import configured_checkpointer
from agent_langgraph.output_utils import (
    content_blocks_to_markdown,
    save_to_markdown_file,
)

# Load environment variables from .env file
load_dotenv()

SKILLS_DIRECTORY = Path(__file__).parent / "skills"

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


def discover_skills() -> dict[str, dict[str, str | Path]]:
    """Discover skill names and short descriptions without adding their full content to the prompt."""
    skills: dict[str, dict[str, str | Path]] = {}
    for skill_file in sorted(SKILLS_DIRECTORY.glob("*/SKILL.md")):
        lines = skill_file.read_text(encoding="utf-8").splitlines()
        skill_name = skill_file.parent.name
        description = ""
        body_start = 0

        if lines and lines[0].strip() == "---":
            # The full content starts from the next line of closing "---".
            # Find body_start for reading name, description before it, and reading full content after it.
            try:
                body_start = next(
                    index for index, line in enumerate(lines[1:], start=1)
                    if line.strip() == "---"
                ) + 1
            except StopIteration as exc:
                raise ValueError(f"Unclosed front matter in {skill_file}") from exc

            # Get name and short description
            for line in lines[1:body_start - 1]:
                key, separator, value = line.partition(":")
                if not separator:
                    continue
                value = value.strip().strip("\"'")
                if key.strip() == "name" and value:
                    skill_name = value
                elif key.strip() == "description" and value:
                    description = value

        if not description:
            raise ValueError(f"Skill description is missing in {skill_file}")
        if skill_name in skills:
            raise ValueError(f"Duplicate skill name '{skill_name}' in {skill_file}")

        skills[skill_name] = {"description": description, "path": skill_file}
    return skills


SKILLS = discover_skills()


@tool
def load_skill(skill_name: str) -> str:
    """Load a skill's complete instructions when they are relevant to the request.

    Args:
        skill_name: The exact name of an available skill.
    """
    skill = SKILLS.get(skill_name)
    if skill is None:
        available = ", ".join(sorted(SKILLS)) or "none"
        return f"Skill '{skill_name}' not found. Available skills: {available}"
    skill_content = Path(skill["path"]).read_text(encoding="utf-8").strip()
    return f"Loaded skill: {skill_name}\n\n{skill_content}"


@tool
def list_tools() -> str:
    """List and describe all available tools."""
    available_skills = ", ".join(sorted(SKILLS)) or "none"
    tools_info = f"""
Available Tools:
1. fetch_text_from_url - Fetch the text content from a given URL. Example: "Fetch text from 'https://example.com'"
2. load_skill - Load the full instructions for a relevant skill. Available skills: {available_skills}
3. list_tools - Display this help message listing all available tools.
    """.strip()
    return tools_info


TOOLS = [fetch_text_from_url, load_skill, list_tools]


class AgentManager:
    """Manages agent and model initialization."""

    def __init__(self, use_checkpointer: bool = False, checkpointer=None):
        """Initialize AgentManager, optionally using a LangGraph checkpointer."""
        self.model = init_chat_model(**MODEL_CONFIG)
        if use_checkpointer and checkpointer is None:
            raise ValueError("A checkpointer is required when use_checkpointer is True.")
        self.use_checkpointer = use_checkpointer
        self.checkpointer = checkpointer

    def _system_prompt(self) -> str:
        prompt_file = Path(__file__).parent / "prompt.md"
        prompt = prompt_file.read_text(encoding="utf-8").strip()
        if not SKILLS:
            return prompt

        skills_prompt = "\n".join(
            f"- **{name}**: {skill['description']}"
            for name, skill in sorted(SKILLS.items())
        )
        return f"{prompt}\n\n## Available Skills\n\n{skills_prompt}"

    def create_agent(self):
        """Create a standard LangChain agent."""
        kwargs = {
            "model": self.model,
            "tools": TOOLS,
            "system_prompt": self._system_prompt(),
        }
        if self.use_checkpointer:
            kwargs["checkpointer"] = self.checkpointer
        return create_agent(**kwargs)

    def create_deep_agent(self):
        """Create a DeepAgents agent."""
        kwargs = {
            "model": self.model,
            "tools": TOOLS,
            "system_prompt": self._system_prompt(),
        }
        if self.use_checkpointer:
            kwargs["checkpointer"] = self.checkpointer
        return create_deep_agent(**kwargs)


def collect_ai_news(thread_id: str | None = None):
    """Collect and save an AI news digest using the relevant available skill."""
    thread_id = thread_id or os.getenv("AGENT_SESSION_ID", "ai-news")
    with configured_checkpointer() as checkpointer:
        manager = AgentManager(use_checkpointer=True, checkpointer=checkpointer)
        deep_agent = manager.create_deep_agent()

        print("Running collect_ai_news...", flush=True)
        deep_agent_result = deep_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Collect the latest AI news digest. Find and load the relevant "
                            "available skill, follow its instructions, and use the provided "
                            "tools to gather and summarize the source material."
                        ),
                    }
                ]
            },
            config={"configurable": {"thread_id": thread_id}},
        )
        result = deep_agent_result["messages"][-1].content_blocks
    
    # Convert to markdown format
    markdown_content = content_blocks_to_markdown(result)
    
    # Save to file with today's date
    filepath = save_to_markdown_file(markdown_content)
    
    print(f"Output saved to: {filepath}")


def ask_agent(question: str, thread_id: str | None = None):
    """Ask the agent a question and print the response."""

    thread_id = thread_id or os.getenv("AGENT_SESSION_ID", "default")
    with configured_checkpointer() as checkpointer:
        manager = AgentManager(use_checkpointer=True, checkpointer=checkpointer)
        agent = manager.create_deep_agent()

        agent_result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"configurable": {"thread_id": thread_id}},
        )
        result = agent_result["messages"][-1].content_blocks

    # Format output as proper JSON with double quotes
    print(
        json.dumps(result, indent=2, ensure_ascii=False)
    )


def main():
    parser = argparse.ArgumentParser(description="Run the skill-enabled agent.")
    parser.add_argument(
        "--thread",
        dest="thread_id",
        help="Thread ID to associate with the request.",
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
