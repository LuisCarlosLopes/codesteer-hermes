import os
import sys
import yaml
import argparse
from pathlib import Path
import importlib

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

def load_yaml(path):
    if not os.path.exists(path): return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}

def get_adapter(ide_name, ide_config):
    module_name = ide_name.replace('-', '_')
    try:
        module = importlib.import_module(f"adapters.{module_name}")
        return module.Adapter(ide_name, ide_config, BASE_DIR, ROOT_DIR)
    except Exception as e:
        print(f"Erro ao carregar adapter para {ide_name}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ide", type=str)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    # Append adapters to sys.path so we can import them
    sys.path.append(str(BASE_DIR / 'deploy'))

    print("Iniciando deploy HERMES...")
    if args.dry_run:
        print("[DRY-RUN] Nenhuma alteração será escrita no disco.")

    config = load_yaml(BASE_DIR / 'deploy' / 'config.yaml')
    targets = config.get('targets', {})
    
    agents = [f.stem for f in (BASE_DIR / 'agents').glob('*.md')]
    skills = [d.name for d in (BASE_DIR / 'skills').iterdir() if d.is_dir()]

    if args.ide:
        if args.ide in targets:
            adapter = get_adapter(args.ide, targets[args.ide])
            if adapter and targets[args.ide].get('enabled'):
                adapter.deploy(agents, skills, args.dry_run)
        else:
            print(f"IDE {args.ide} not found in config.")
    else:
        for ide_name, ide_config in targets.items():
            if not ide_config.get('enabled'): continue
            adapter = get_adapter(ide_name, ide_config)
            if adapter:
                adapter.deploy(agents, skills, args.dry_run)

    print("Deploy finalizado com sucesso.")

if __name__ == "__main__":
    main()
