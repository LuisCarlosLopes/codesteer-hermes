import argparse
import re
from pathlib import Path

import yaml


RAW_SECTIONS = [
    "## Resumo do que foi analisado",
    "## Fontes e evidências",
    "## Conteúdo extraído",
    "## Itens inferidos e não verificados",
    "## Conflitos, bloqueios e perguntas abertas",
]

CONSOLIDATED_SECTIONS = [
    "## Escopo consolidado",
    "## Evidências consolidadas",
    "## Conteúdo reconciliado",
    "## Itens pendentes de validação",
    "## Conflitos e gaps relacionados",
]

SPECIAL_FILES = {
    "gaps.md": ["# Gaps", "## Resumo", "## Lista de gaps", "## Decisões de consolidação impactadas"],
    "synthesis-report.md": [
        "# Synthesis Report",
        "## Resumo executivo",
        "## Cobertura consolidada por domínio",
        "## Conflitos reconciliados",
        "## Pendências para checkpoint HITL",
    ],
    "remediation-requests.md": ["# Remediation Requests", "## Resumo", "## Pedidos"],
    "validation-report.md": [
        "# Validation Report",
        "## Resumo",
        "## Checklist por categoria",
        "## Riscos residuais",
        "## Recomendação do Validator",
    ],
    "user-confirmation.md": ["# User Confirmation", "## Estado", "## Checkpoint apresentado", "## Resposta do usuário"],
    "rebuild-readiness-report.md": [
        "# Rebuild Readiness Report",
        "## Resumo",
        "## Avaliação por dimensão",
        "## Bloqueios e lacunas",
        "## Recomendação",
    ],
}

ALLOWED_PHASES = {"intake", "exploration", "analysis", "synthesis", "validation", "documentation"}
ALLOWED_SESSION_STATUS = {"in_progress", "validated", "sdd_ready", "blocked", "archived"}
ALLOWED_VALIDATION_GATES = {"not_started", "pending", "passed", "failed", "blocked_by_rebuild_readiness"}
ALLOWED_TOP_LEVEL_STATUS = {"pending", "approved", "needs_revision"}
ALLOWED_REBUILD_STATUS = {"ready", "partial", "blocked"}
REQUIRED_BY_LEVEL = {
    "L1": ["screen-inventory.md", "navigation-graph.md", "tech-stack.md", "code-structure.md", "db-schema.md"],
    "L2": [
        "screen-inventory.md",
        "navigation-graph.md",
        "tech-stack.md",
        "code-structure.md",
        "db-schema.md",
        "api-contracts.md",
        "business-rules.md",
        "component-map.md",
        "state-map.md",
        "design-overview.md",
    ],
    "L3": [
        "screen-inventory.md",
        "navigation-graph.md",
        "tech-stack.md",
        "code-structure.md",
        "db-schema.md",
        "api-contracts.md",
        "business-rules.md",
        "component-map.md",
        "state-map.md",
        "design-overview.md",
        "security-model.md",
        "pii-map.md",
        "design-tokens.md",
        "rebuild-readiness-report.md",
    ],
}

GENERIC_EVIDENCE_PATTERNS = [
    re.compile(r"^na UI$", re.IGNORECASE),
    re.compile(r"^na API$", re.IGNORECASE),
    re.compile(r"^no código$", re.IGNORECASE),
    re.compile(r"^na interface$", re.IGNORECASE),
    re.compile(r"^no sistema$", re.IGNORECASE),
]


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def headings_in_order(content):
    headings = []
    for line in content.splitlines():
        if line.startswith("#"):
            headings.append(line.strip())
    return headings


def validate_required_sections(path):
    content = path.read_text(encoding="utf-8")
    headings = headings_in_order(content)
    filename = path.name

    if filename in SPECIAL_FILES:
        required = SPECIAL_FILES[filename]
    elif "/raw/" in str(path).replace("\\", "/"):
        required = RAW_SECTIONS
    else:
        required = CONSOLIDATED_SECTIONS

    errors = []
    positions = []
    for heading in required:
        if heading not in headings:
            errors.append(f"{path}: seção obrigatória ausente: {heading}")
            continue
        positions.append(headings.index(heading))

    if positions and positions != sorted(positions):
        errors.append(f"{path}: seções obrigatórias fora de ordem.")

    return errors


def validate_evidence_lines(path):
    errors = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip().strip("|").strip()
        if not stripped:
            continue
        if "evidência" not in stripped.lower():
            continue
        value = stripped.split(":", 1)[-1].strip() if ":" in stripped else stripped
        for pattern in GENERIC_EVIDENCE_PATTERNS:
            if pattern.match(value):
                errors.append(f"{path}: evidência genérica não localizável: `{value}`")
                break
    return errors


def validate_session_yaml(path):
    payload = load_yaml(path)
    errors = []

    required = {
        "schema_version",
        "scope_slug",
        "target",
        "target_type",
        "level",
        "source",
        "created_at",
        "agents_active",
        "phases_completed",
        "current_phase",
        "status",
        "phase_history",
        "validation_gate",
        "hermes_root",
        "scope_path",
        "glossary_path",
    }
    missing = sorted(required - set(payload))
    if missing:
        errors.append(f"{path}: campos obrigatórios ausentes: {', '.join(missing)}")
        return errors

    if payload["current_phase"] not in ALLOWED_PHASES:
        errors.append(f"{path}: current_phase inválido: {payload['current_phase']}")

    if payload["status"] not in ALLOWED_SESSION_STATUS:
        errors.append(f"{path}: status inválido: {payload['status']}")

    if payload["validation_gate"] not in ALLOWED_VALIDATION_GATES:
        errors.append(f"{path}: validation_gate inválido: {payload['validation_gate']}")

    if not isinstance(payload["agents_active"], list) or not payload["agents_active"]:
        errors.append(f"{path}: agents_active deve ser lista não vazia.")

    if not isinstance(payload["phases_completed"], list):
        errors.append(f"{path}: phases_completed deve ser lista.")

    if not set(payload["phases_completed"]).issubset(ALLOWED_PHASES - {"documentation"}):
        errors.append(f"{path}: phases_completed contém fase inválida.")

    phase_history = payload["phase_history"]
    if not isinstance(phase_history, list) or not phase_history:
        errors.append(f"{path}: phase_history deve ser lista não vazia.")
    else:
        for entry in phase_history:
            if not isinstance(entry, dict):
                errors.append(f"{path}: phase_history deve conter objetos.")
                continue
            if {"phase", "status", "at"} - set(entry):
                errors.append(f"{path}: phase_history possui item incompleto: {entry}")
                continue
            if entry["phase"] not in ALLOWED_PHASES:
                errors.append(f"{path}: phase_history contém fase inválida: {entry['phase']}")

    return errors


def validate_validation_report(path):
    content = path.read_text(encoding="utf-8")
    errors = validate_required_sections(path)
    allowed_statuses = {"OK", "ALERTA", "FALHA", "NÃO APLICÁVEL"}
    statuses = set(re.findall(r"\|\s*(OK|ALERTA|FALHA|NÃO APLICÁVEL)\s*\|", content))
    if not statuses:
        errors.append(f"{path}: validation-report.md precisa registrar ao menos um status de checklist.")
    if statuses - allowed_statuses:
        errors.append(f"{path}: validation-report.md contém status inválido.")
    return errors


def validate_user_confirmation(path):
    content = path.read_text(encoding="utf-8")
    errors = validate_required_sections(path)
    matches = re.findall(r"- Status:\s*(\S+)", content)
    if not matches:
        errors.append(f"{path}: user-confirmation.md precisa declarar Status.")
    elif matches[0] not in ALLOWED_TOP_LEVEL_STATUS:
        errors.append(f"{path}: Status inválido em user-confirmation.md: {matches[0]}")
    return errors


def validate_rebuild_readiness(path):
    content = path.read_text(encoding="utf-8")
    errors = validate_required_sections(path)
    matches = re.findall(r"- Status:\s*(\S+)", content)
    if not matches:
        errors.append(f"{path}: rebuild-readiness-report.md precisa declarar Status.")
    elif matches[0] not in ALLOWED_REBUILD_STATUS:
        errors.append(f"{path}: Status inválido em rebuild-readiness-report.md: {matches[0]}")
    return errors


def validate_markdown(path):
    if path.name in {"README.md", "scope.md", "glossary.md"}:
        return []
    if path.name == "validation-report.md":
        return validate_validation_report(path)
    if path.name == "user-confirmation.md":
        return validate_user_confirmation(path)
    if path.name == "rebuild-readiness-report.md":
        return validate_rebuild_readiness(path)

    errors = validate_required_sections(path)
    errors.extend(validate_evidence_lines(path))
    return errors


def validate_session_directory(path):
    errors = []
    session_file = path / "session.yaml"
    session_payload = None
    if session_file.exists():
        session_payload = load_yaml(session_file)
        errors.extend(validate_session_yaml(session_file))
    else:
        errors.append(f"{path}: session.yaml ausente.")

    if session_payload:
        required_files = list(REQUIRED_BY_LEVEL.get(session_payload.get("level"), []))
        if session_payload.get("level") == "L3" and session_payload.get("validation_gate") != "passed":
            required_files = [name for name in required_files if name != "rebuild-readiness-report.md"]
        for filename in required_files:
            if not (path / filename).exists():
                errors.append(f"{path}: artefato obrigatório ausente para {session_payload.get('level')}: {filename}")

    for artifact in sorted(path.rglob("*.md")):
        if "/sdd/" in str(artifact).replace("\\", "/"):
            continue
        errors.extend(validate_markdown(artifact))

    return errors


def validate_path(path):
    path = Path(path)
    if path.is_dir():
        return validate_session_directory(path)
    if path.name == "session.yaml":
        return validate_session_yaml(path)
    if path.suffix == ".md":
        return validate_markdown(path)
    return [f"{path}: tipo de arquivo não suportado para validação."]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validador executável do contrato HERMES.")
    parser.add_argument("paths", nargs="+", help="Arquivos ou diretórios a validar.")
    args = parser.parse_args(argv)

    errors = []
    for raw_path in args.paths:
        errors.extend(validate_path(raw_path))

    if errors:
        for error in errors:
            print(f"[ERRO] {error}")
        return 1

    print("Validação HERMES concluída sem erros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
