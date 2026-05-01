import os
import yaml
import shutil
from pathlib import Path

class BaseAdapter:
    def __init__(self, ide_name, config, base_dir, root_dir):
        self.ide_name = ide_name
        self.config = config
        self.base_dir = Path(base_dir)
        self.root_dir = Path(root_dir)

    def load_yaml(self, path):
        if not os.path.exists(path): return {}
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}

    def generate_frontmatter(self, defaults, specific):
        merged = {**defaults, **specific}
        return f"---\n{yaml.dump(merged)}---\n"

    def validate(self):
        if not (self.base_dir / 'agents').exists():
            print(f"[{self.ide_name}] Erro: Diretório canônico de agentes não encontrado.")
            return False
        if not (self.base_dir / 'skills').exists():
            print(f"[{self.ide_name}] Erro: Diretório canônico de skills não encontrado.")
            return False
        return True

    def deploy_agents(self, agents, dry_run=False):
        agents_dir = self.root_dir / self.config['agents_dir']
        if not dry_run:
            agents_dir.mkdir(parents=True, exist_ok=True)
            
        ide_defaults_path = self.base_dir / 'ide-configs' / self.ide_name / '_defaults.yaml'
        defaults = self.load_yaml(ide_defaults_path)
        
        for agent in agents:
            agent_config_path = self.base_dir / 'ide-configs' / self.ide_name / f"{agent}.yaml"
            agent_md_path = self.base_dir / 'agents' / f"{agent}.md"
            
            specific = self.load_yaml(agent_config_path)
            frontmatter = self.generate_frontmatter(defaults, specific)
            
            body = ""
            if agent_md_path.exists():
                body = agent_md_path.read_text()
                
            final_content = frontmatter + "\n" + body
            
            suffix = self.config.get('skill_suffix', '.md')
            
            # Special case for Claude
            if self.ide_name == "claude-code":
                target_path = agents_dir / f"{agent}.md"
            else:
                target_path = agents_dir / f"hermes-{agent}{suffix}"
            
            if not dry_run:
                target_path.write_text(final_content)
            print(f"  [Agent] Written to {target_path.relative_to(self.root_dir)}")

    def deploy_skills(self, skills, dry_run=False):
        skills_dir = self.root_dir / self.config['skills_dir']
        if not dry_run:
            skills_dir.mkdir(parents=True, exist_ok=True)
        
        for skill in skills:
            source = self.base_dir / 'skills' / skill
            target = skills_dir / f"hermes-{skill}"
            
            if not dry_run:
                if target.is_symlink() or target.exists():
                    if target.is_symlink(): target.unlink()
                    elif target.is_dir(): shutil.rmtree(target)
                    else: target.unlink()
                rel_path = os.path.relpath(source, target.parent)
                os.symlink(rel_path, target)
            print(f"  [Skill] Symlinked {target.relative_to(self.root_dir)} -> {source.relative_to(self.root_dir)}")

    def create_main_symlinks(self, dry_run=False):
        pass
        
    def deploy(self, agents, skills, dry_run=False):
        print(f"Deploying for IDE: {self.ide_name}")
        if not self.validate(): return
        self.deploy_agents(agents, dry_run)
        self.deploy_skills(skills, dry_run)
        self.create_main_symlinks(dry_run)
