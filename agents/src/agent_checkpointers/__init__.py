"""Shared checkpointer configuration for the agent applications."""

import os
from contextlib import contextmanager, nullcontext
from urllib.parse import quote

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

# Load .env before capturing the environment flag at import time.
load_dotenv()

# Set SUPPORT_DB_CHECKPOINTER=true to enable the database checkpointer.
SUPPORT_DB_CHECKPOINTER = (
    os.getenv("SUPPORT_DB_CHECKPOINTER", "false").strip().lower()
    in {"1", "true", "yes", "on"}
)
IN_MEMORY_CHECKPOINTER = InMemorySaver()


def _postgres_uri() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "agent")
    user = quote(os.getenv("POSTGRES_USER", "postgres"), safe="")
    password = quote(os.getenv("POSTGRES_PASSWORD", "postgres"), safe="")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


@contextmanager
def _postgres_checkpointer():
    """Open the Postgres saver and ensure its checkpoint tables exist."""
    with PostgresSaver.from_conn_string(_postgres_uri()) as checkpointer:
        checkpointer.setup()
        yield checkpointer


def configured_checkpointer():
    """Return a context manager for the checkpointer selected by the environment."""
    if SUPPORT_DB_CHECKPOINTER:
        print("Using Postgres checkpointer for memory persistence.")
        return _postgres_checkpointer()

    print("Using in-memory checkpointer for memory persistence.")
    return nullcontext(IN_MEMORY_CHECKPOINTER)
