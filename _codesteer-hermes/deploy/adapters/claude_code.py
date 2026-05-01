from .base import BaseAdapter


class Adapter(BaseAdapter):
    bootstrap_links = (
        ("AGENTS.md", "_codesteer-hermes/AGENTS.md"),
        ("CLAUDE.md", "AGENTS.md"),
    )

    def agent_filename(self, agent):
        return f"{agent}.md"
