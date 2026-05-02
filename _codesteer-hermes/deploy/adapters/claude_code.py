from .base import BaseAdapter


class Adapter(BaseAdapter):
    bootstrap_links = ()

    def agent_filename(self, agent):
        return f"{agent}.md"
