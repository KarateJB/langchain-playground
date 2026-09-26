"""Utilities for output formatting and file handling."""

import json
from datetime import datetime
from pathlib import Path


def content_blocks_to_markdown(content_blocks: list) -> str:
    """Convert content blocks JSON to markdown format.

    Args:
        content_blocks: List of content block dictionaries

    Returns:
        Formatted markdown string
    """
    markdown_parts = []

    for block in content_blocks:
        if isinstance(block, dict):
            block_type = block.get("type", "unknown")

            # Extract signature from extras if present
            signature = block.get("extras", {}).get("signature", "")

            markdown_parts.append("## Metadata\n")
            markdown_parts.append(f"- block_type: {block_type.upper()}")
            markdown_parts.append(f"- signature: {signature}")
            markdown_parts.append("\n")
            markdown_parts.append("## Result\n")

            if block_type == "text":
                text = block.get("text", "")
                markdown_parts.append(text)
            else:
                # For other block types, add a header and the content
                markdown_parts.append(json.dumps(block, indent=2, ensure_ascii=False))
        else:
            markdown_parts.append(str(block))

    return "\n".join(markdown_parts)


def save_to_markdown_file(content: str, output_dir: str = "outputs") -> str:
    """Save content to a markdown file with today's date.

    Args:
        content: Content to save
        output_dir: Subdirectory name for outputs (relative to script directory)

    Returns:
        Path to the saved file
    """
    script_dir = Path(__file__).parent
    output_path = script_dir / output_dir
    output_path.mkdir(exist_ok=True)

    # Create filename with today's date (yyyyMMdd format)
    today = datetime.now().strftime("%Y%m%d")
    filepath = output_path / f"output_{today}.md"

    # Write to file (overwrite if exists)
    filepath.write_text(content, encoding="utf-8")

    return str(filepath)
