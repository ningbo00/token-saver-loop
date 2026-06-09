"""Built-in format templates for structured output."""

TEMPLATES: dict[str, str] = {
    "json": (
        "Convert the following input into valid JSON. "
        "Do not include explanations or markdown code fences outside the JSON content."
    ),
    "yaml": (
        "Convert the following input into valid YAML. "
        "Do not include explanations or markdown code fences outside the YAML content."
    ),
    "markdown-table": (
        "Convert the following input into a Markdown table. "
        "Do not include explanations outside the table."
    ),
    "todo-list": (
        "Convert the following input into a Markdown todo list. "
        "Use - [ ] for incomplete items and - [x] for completed items if applicable. "
        "Do not include explanations outside the list."
    ),
}


def get_template(format_name: str) -> str:
    """Return the system prompt template for the given format."""
    if format_name not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES))
        raise ValueError(f"Unknown format: {format_name!r}. Available: {available}")
    return TEMPLATES[format_name]


def list_templates() -> list[str]:
    """Return a list of available format names."""
    return list(TEMPLATES.keys())
