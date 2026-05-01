from .base import BaseAdapter


class Adapter(BaseAdapter):
    bootstrap_links = (("CLAUDE.md", "_codesteer-hermes/AGENTS.md"),)

    def agent_filename(self, agent):
        return f"{agent}.md"
