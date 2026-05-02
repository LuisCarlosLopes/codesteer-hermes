import hashlib
import os
from pathlib import Path

import yaml


class BaseAdapter:
    contract_version = "hermes-deploy-v1"
    bootstrap_links = ()

    def __init__(self, ide_name, config, base_dir, root_dir):
        self.ide_name = ide_name
        self.config = config
        self.base_dir = Path(base_dir)
        self.root_dir = Path(root_dir)

    def load_yaml(self, path):
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def generate_frontmatter(self, defaults, specific):
        merged = {**defaults, **specific}
        cleaned = {key: value.strip() if isinstance(value, str) else value for key, value in merged.items()}
        return f"---\n{yaml.safe_dump(cleaned, allow_unicode=True, sort_keys=False)}---\n"

    def validate(self):
        errors = []
        if not (self.base_dir / "agents").exists():
            errors.append(f"[{self.ide_name}] Diretório canônico de agentes não encontrado.")
        if not (self.base_dir / "skills").exists():
            errors.append(f"[{self.ide_name}] Diretório canônico de skills não encontrado.")
        if "agents_dir" not in self.config or "skills_dir" not in self.config:
            errors.append(f"[{self.ide_name}] Configuração incompleta: agents_dir e skills_dir são obrigatórios.")
        return errors

    def sha256_text(self, content):
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def relative_link_target(self, source, destination_parent):
        return os.path.relpath(source, destination_parent)

    def default_agent_filename(self, agent):
        suffix = self.config.get("agent_suffix", self.config.get("skill_suffix", ".md"))
        prefix = self.config.get("agent_prefix", self.config.get("skill_prefix", "hermes-"))
        if agent == "hermes":
            primary_name = self.config.get("primary_agent_name", "hermes")
            return f"{primary_name}{suffix}"
        return f"{prefix}{agent}{suffix}"

    def agent_filename(self, agent):
        return self.default_agent_filename(agent)

    def skill_link_name(self, skill):
        prefix = self.config.get("skill_prefix", "hermes-")
        without = self.config.get("skills_without_prefix") or ()
        # Pastas já prefixadas com "hermes-" (ex.: hermes-help) evitam symlink hermes-hermes-* .
        if skill.startswith("hermes-"):
            return skill
        if skill in without:
            return skill
        return f"{prefix}{skill}"

    def render_agent(self, agent):
        ide_defaults_path = self.base_dir / "ide-configs" / self.ide_name / "_defaults.yaml"
        defaults = self.load_yaml(ide_defaults_path)
        specific = self.load_yaml(self.base_dir / "ide-configs" / self.ide_name / f"{agent}.yaml")
        body = (self.base_dir / "agents" / f"{agent}.md").read_text(encoding="utf-8")
        return self.generate_frontmatter(defaults, specific) + "\n" + body

    def plan_agent_operation(self, agent):
        target_path = self.root_dir / self.config["agents_dir"] / self.agent_filename(agent)
        content = self.render_agent(agent)
        return {
            "kind": "agent",
            "path": str(target_path),
            "source": str((self.base_dir / "agents" / f"{agent}.md").relative_to(self.root_dir)),
            "signature": self.sha256_text(content),
            "content": content,
        }

    def plan_skill_operation(self, skill):
        source = self.base_dir / "skills" / skill
        target = self.root_dir / self.config["skills_dir"] / self.skill_link_name(skill)
        link_target = self.relative_link_target(source, target.parent)
        return {
            "kind": "skill",
            "path": str(target),
            "source": str(source.relative_to(self.root_dir)),
            "signature": self.sha256_text(link_target),
            "link_target": link_target,
        }

    def plan_bootstrap_operations(self):
        operations = []
        for relative_path, target_reference in self.bootstrap_links:
            destination = self.root_dir / relative_path
            target = self.root_dir / target_reference
            link_target = self.relative_link_target(target, destination.parent)
            operations.append(
                {
                    "kind": "bootstrap",
                    "path": str(destination),
                    "source": target_reference,
                    "signature": self.sha256_text(link_target),
                    "link_target": link_target,
                }
            )
        return operations

    def plan_operations(self, agents, skills):
        operations = [self.plan_agent_operation(agent) for agent in agents]
        operations.extend(self.plan_skill_operation(skill) for skill in skills)
        operations.extend(self.plan_bootstrap_operations())
        return operations
