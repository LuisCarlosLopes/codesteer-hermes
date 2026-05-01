from .base import BaseAdapter


class Adapter(BaseAdapter):
    bootstrap_links = (
        ("AGENTS.md", "_codesteer-hermes/AGENTS.md"),
        (".github/copilot-instructions.md", "AGENTS.md"),
    )
