import argparse
import hashlib
import importlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


DEPLOY_SCHEMA_VERSION = 1
DEPLOY_CONTRACT_VERSION = "hermes-deploy-v1"

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
DEPLOY_LOG_PATH = ROOT_DIR / ".deploy-log.yaml"
SESSIONS_INDEX_PATH = ROOT_DIR / "_hermes" / ".sessions-index.yaml"


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_yaml(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)


def sha256_text(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def relative_path(path):
    return str(path.relative_to(ROOT_DIR))


def get_adapter(ide_name, ide_config):
    module_name = ide_name.replace("-", "_")
    module = importlib.import_module(f"adapters.{module_name}")
    return module.Adapter(ide_name, ide_config, BASE_DIR, ROOT_DIR)


def load_deploy_log():
    payload = load_yaml(DEPLOY_LOG_PATH)
    if not payload:
        return {
            "schema_version": DEPLOY_SCHEMA_VERSION,
            "contract_version": DEPLOY_CONTRACT_VERSION,
            "updated_at": None,
            "targets": {},
            "runs": [],
        }

    payload.setdefault("schema_version", DEPLOY_SCHEMA_VERSION)
    payload.setdefault("contract_version", DEPLOY_CONTRACT_VERSION)
    payload.setdefault("updated_at", None)
    payload.setdefault("targets", {})
    payload.setdefault("runs", [])
    return payload


def ensure_hermes_root(validate_only=False, dry_run=False):
    hermes_dir = ROOT_DIR / "_hermes"

    if validate_only:
        issues = []
        if not hermes_dir.exists():
            issues.append("Diretório _hermes/ ausente.")
        if not SESSIONS_INDEX_PATH.exists():
            issues.append("_hermes/.sessions-index.yaml ausente.")
        else:
            data = load_yaml(SESSIONS_INDEX_PATH)
            if not isinstance(data.get("sessions"), list):
                issues.append("_hermes/.sessions-index.yaml deve conter a chave `sessions` como lista.")
        return issues

    if dry_run:
        print("[DRY-RUN] Verificaria _hermes/ e _hermes/.sessions-index.yaml.")
        return []

    hermes_dir.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_INDEX_PATH.exists():
        dump_yaml(SESSIONS_INDEX_PATH, {"sessions": []})
        print("[Hermes] Criado _hermes/.sessions-index.yaml")
    else:
        data = load_yaml(SESSIONS_INDEX_PATH)
        if not isinstance(data.get("sessions"), list):
            raise ValueError("_hermes/.sessions-index.yaml precisa conter `sessions` como lista.")
        print("[Hermes] _hermes/.sessions-index.yaml já existe — mantido.")
    return []


def get_actual_signature(operation):
    path = Path(operation["path"])
    kind = operation["kind"]

    if not path.exists() and not path.is_symlink():
        return None

    if kind in {"skill", "bootstrap"}:
        if not path.is_symlink():
            return {"kind": kind, "signature": None, "is_symlink": False}
        target = os.readlink(path)
        return {"kind": kind, "signature": sha256_text(target), "is_symlink": True}

    content = path.read_text(encoding="utf-8")
    return {"kind": kind, "signature": sha256_text(content), "is_symlink": False}


def classify_operation(operation, target_state, force):
    path = operation["path"]
    desired_signature = operation["signature"]
    previous_entry = target_state.get(path)
    actual = get_actual_signature(operation)

    if actual and actual["signature"] == desired_signature:
        return "unchanged", actual

    if actual is None:
        return "create", actual

    previous_signature = previous_entry.get("signature") if previous_entry else None
    if previous_signature and actual["signature"] == previous_signature:
        return "update", actual

    if force:
        return "force", actual

    if previous_entry is None:
        return "conflict", actual

    return "drift", actual


def apply_operation(operation, status, dry_run):
    path = Path(operation["path"])
    if dry_run:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    if operation["kind"] in {"skill", "bootstrap"}:
        if path.exists() or path.is_symlink():
            if path.is_dir() and not path.is_symlink():
                raise ValueError(f"Destino de symlink é um diretório real: {path}")
            path.unlink()
        os.symlink(operation["link_target"], path)
        return

    if path.is_symlink():
        path.unlink()
    path.write_text(operation["content"], encoding="utf-8")


def record_run(log_payload, ide_name, mode, results):
    summary = {
        "timestamp": utc_now(),
        "ide": ide_name,
        "mode": mode,
        "created": results.count("create"),
        "updated": results.count("update"),
        "forced": results.count("force"),
        "unchanged": results.count("unchanged"),
        "conflicted": results.count("conflict"),
        "drifted": results.count("drift"),
        "status": "error" if "drift" in results else ("warning" if "conflict" in results else "ok"),
    }
    log_payload["runs"].append(summary)
    log_payload["runs"] = log_payload["runs"][-50:]
    log_payload["updated_at"] = summary["timestamp"]


def process_target(adapter, agents, skills, args, log_payload):
    plan_only = getattr(args, "plan_only", False)
    operations = adapter.plan_operations(agents, skills)
    target_state = log_payload.setdefault("targets", {}).setdefault(adapter.ide_name, {}).setdefault("files", {})

    results = []
    errors = []
    warnings = []
    next_state = dict(target_state)
    operation_reports = []

    for operation in operations:
        status, actual = classify_operation(operation, target_state, args.force)
        results.append(status)

        label = f"[{adapter.ide_name}] {status.upper()} {relative_path(Path(operation['path']))}"
        report = {
            "status": status,
            "kind": operation["kind"],
            "path": operation["path"],
            "source": operation["source"],
            "signature": operation["signature"],
            "actual_signature": actual["signature"] if actual else None,
            "previous_signature": target_state.get(operation["path"], {}).get("signature"),
        }
        if status == "drift":
            report["message"] = (
                f"{label} — conteúdo atual diverge do último deploy conhecido"
                f" (anterior={report['previous_signature']}, atual={actual['signature']}, desejado={operation['signature']})."
            )
            errors.append(report["message"])
            print(label)
            operation_reports.append(report)
            continue

        if status == "conflict":
            report["message"] = (
                f"{label} — arquivo preexistente não gerenciado foi preservado"
                f" (atual={actual['signature']}, desejado={operation['signature']})."
            )
            warnings.append(report["message"])
            print(label)
            operation_reports.append(report)
            continue

        print(label)
        if not args.validate and not plan_only:
            apply_operation(operation, status, args.dry_run)

        next_state[operation["path"]] = {
            "kind": operation["kind"],
            "source": operation["source"],
            "signature": operation["signature"],
        }
        operation_reports.append(report)

    if not args.validate and not args.dry_run and not plan_only and not errors:
        planned_paths = {op["path"] for op in operations}
        for path in list(next_state.keys()):
            if path in planned_paths:
                continue
            meta = next_state[path]
            if meta.get("kind") != "agent":
                continue
            del next_state[path]
            orphan = Path(path)
            if orphan.is_file():
                orphan.unlink()
                print(f"[{adapter.ide_name}] REMOVE {relative_path(orphan)}")

        log_payload["targets"][adapter.ide_name]["files"] = next_state
        record_run(log_payload, adapter.ide_name, "force" if args.force else "deploy", results)

    if args.validate:
        record_run(log_payload, adapter.ide_name, "validate", results)

    return {
        "ide": adapter.ide_name,
        "operations": operation_reports,
        "errors": errors,
        "warnings": warnings,
    }


def deploy_target(adapter, agents, skills, args, log_payload):
    return process_target(adapter, agents, skills, args, log_payload)["errors"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ide", action="append")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--summary-json", type=str)
    args = parser.parse_args()

    sys.path.append(str(BASE_DIR / "deploy"))

    print("Iniciando deploy HERMES...")
    if args.dry_run:
        print("[DRY-RUN] Nenhuma alteração será escrita no disco.")
    if args.validate:
        print("[VALIDATE] Apenas auditoria do deploy e da estrutura base será executada.")

    issues = ensure_hermes_root(validate_only=args.validate, dry_run=args.dry_run)
    for issue in issues:
        print(f"[ERRO] {issue}")

    config = load_yaml(BASE_DIR / "deploy" / "config.yaml")
    targets = config.get("targets", {})
    agents = sorted(f.stem for f in (BASE_DIR / "agents").glob("*.md"))
    skills = sorted(d.name for d in (BASE_DIR / "skills").iterdir() if d.is_dir())
    log_payload = load_deploy_log()

    target_names = args.ide if args.ide else [name for name, conf in targets.items() if conf.get("enabled")]
    target_results = []

    for ide_name in target_names:
        if ide_name not in targets:
            issues.append(f"IDE {ide_name} não encontrada em config.yaml.")
            continue

        try:
            adapter = get_adapter(ide_name, targets[ide_name])
        except Exception as exc:
            issues.append(f"Erro ao carregar adapter para {ide_name}: {exc}")
            continue

        validation_errors = adapter.validate()
        issues.extend(validation_errors)
        if validation_errors:
            continue

        result = process_target(adapter, agents, skills, args, log_payload)
        target_results.append(result)
        issues.extend(result["errors"])

    if not args.validate and not args.dry_run and not args.plan_only and not issues:
        dump_yaml(DEPLOY_LOG_PATH, log_payload)
        print(f"[Hermes] Deploy log atualizado em {relative_path(DEPLOY_LOG_PATH)}")

    if args.summary_json:
        Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.summary_json, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "schema_version": DEPLOY_SCHEMA_VERSION,
                    "contract_version": DEPLOY_CONTRACT_VERSION,
                    "root_dir": str(ROOT_DIR),
                    "mode": "plan"
                    if args.plan_only
                    else ("validate" if args.validate else ("dry-run" if args.dry_run else "deploy")),
                    "targets": target_results,
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )

    if issues:
        print("Deploy finalizado com pendências.")
        return 1

    print("Deploy finalizado com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
