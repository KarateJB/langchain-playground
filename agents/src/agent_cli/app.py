import argparse
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from agent_langgraph.output_utils import configure_utf8_streams

APP = "agent-skills"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_agent_command(question: str | None, thread_id: str) -> list[str]:
    """Build the existing agent command for one turn."""
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("Could not find 'uv' on PATH. Install uv or add it to PATH.")

    command = [
        uv,
        "run",
        "--project",
        str(PROJECT_ROOT),
        APP,
        "--thread",
        thread_id,
    ]
    if question is not None:
        command.append(question)
    return command


def parse_agent_output(output: str) -> str:
    """Extract and render the JSON content blocks printed by the agent."""
    decoder = json.JSONDecoder()
    parsed_candidates: list[tuple[int, list[object]]] = []

    for position, character in enumerate(output):
        if character != "[":
            continue
        try:
            payload, end = decoder.raw_decode(output, position)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            parsed_candidates.append((end - position, payload))

    if not parsed_candidates:
        raise ValueError("The agent command did not return a JSON content-block list.")

    content_blocks = max(parsed_candidates, key=lambda candidate: candidate[0])[1]
    answer_parts: list[str] = []
    for block in content_blocks:
        if isinstance(block, str):
            answer_parts.append(block)
        elif isinstance(block, dict):
            text = block.get("text")
            if isinstance(text, str):
                answer_parts.append(text)

    if answer_parts:
        return "\n".join(part for part in answer_parts if part)
    return json.dumps(content_blocks, indent=2, ensure_ascii=False)


def run_agent(question: str | None, thread_id: str) -> str:
    """Run one turn through the existing uv console command."""
    completed_process = subprocess.run(
        build_agent_command(question, thread_id),
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )
    if completed_process.returncode != 0:
        output = completed_process.stderr.strip() or completed_process.stdout.strip()
        if not output:
            output = f"The agent exited with status {completed_process.returncode}."
        raise RuntimeError(output)
    return parse_agent_output(completed_process.stdout)


def display_response(question: str | None, thread_id: str) -> bool:
    """Run a turn and display its answer, returning whether it succeeded."""
    print("Please wait...", flush=True)
    try:
        answer = run_agent(question, thread_id)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return False

    print(answer)
    return True


def main(argv: list[str] | None = None) -> int:
    configure_utf8_streams()
    parser = argparse.ArgumentParser(
        description="Start an interactive session with the LangGraph agent."
    )
    parser.add_argument(
        "--thread",
        dest="thread_id",
        help="Thread ID for loading and saving conversation memory.",
    )
    args = parser.parse_args(argv)
    thread_id = args.thread_id or f"agent-cli-{uuid.uuid4()}"

    if not display_response(None, thread_id):
        return 1

    try:
        while True:
            question = input("> ").strip()
            if question.lower() == "quit" or question.lower() == "exit":
                print("Goodbye.")
                return 0
            if question:
                display_response(question, thread_id)
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
