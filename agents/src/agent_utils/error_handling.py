"""Error-handling decorators for agent applications."""

from collections.abc import Callable
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import ParamSpec

P = ParamSpec("P")


def handle_agent_errors(output_dir: Path):
    """Convert agent errors into a generic response and save the error details."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> list:
            try:
                return func(*args, **kwargs)
            except Exception as error:  # noqa: BLE001
                output_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
                error_file = output_dir / f"error_{timestamp}.txt"
                error_file.write_text(str(error), encoding="utf-8")
                print(error, flush=True)
                return [
                    {
                        "type": "text",
                        "text": "The agent cannot respond now. Please try again later.",
                    }
                ]

        return wrapper

    return decorator
