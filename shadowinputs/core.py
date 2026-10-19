"""Conservative, deliberately limited repository-local approval checks."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Iterable


class ApprovalError(Exception):
    """An approval cannot be established or safely verified."""


def normalize(path: str) -> str:
    if not isinstance(path, str) or not path or '\\' in path or '\x00' in path:
        raise ApprovalError(f"Invalid repository path: {path!r}")
    pure = PurePosixPath(path)
    if pure.is_absolute() or '..' in pure.parts or str(pure) != path or ':' in path:
        raise ApprovalError(f"Unsafe repository path: {path!r}")
    if str(pure) == '.':
        raise ApprovalError("Path must identify a file")
    return pure.as_posix()


def safe_file(root: Path, name: str) -> Path:
    name = normalize(name)
    root = root.resolve()
    current = root
    for part in PurePosixPath(name).parts:
        current = current / part
        if current.is_symlink():
            raise ApprovalError(f"Symlinks are outside this prototype's scope: {name}")
    try:
        current.resolve(strict=True).relative_to(root)
    except (FileNotFoundError, ValueError) as ex:
        raise ApprovalError(f"Missing or out-of-root dependency: {name}") from ex
    if not current.is_file():
        raise ApprovalError(f"Not a regular file: {name}")
    return current


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def literal_path(expr: ast.expr, constants: dict[str, str]) -> str | None:
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return expr.value
    if isinstance(expr, ast.Name):
        return constants.get(expr.id)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in ('Path', 'PurePath') and len(expr.args) == 1:
        return literal_path(expr.args[0], constants)
    return None


def python_read_dependencies(code: str) -> tuple[set[str], list[str]]:
    """Recognize common literal Python file reads. Not a full call graph."""
    tree = ast.parse(code)
    constants: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = literal_path(node.value, constants) if node.value is not None else None
            if value is not None:
                for target in targets:
                    if isinstance(target, ast.Name):
                        constants[target.id] = value
    dependencies: set[str] = set()
    unknown: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = None
        candidate: str | None = None
        if isinstance(node.func, ast.Name) and node.func.id == 'open':
            name = 'open'
            if node.args:
                candidate = literal_path(node.args[0], constants)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in ('read_text', 'read_bytes', 'open'):
            # Path('x').read_text() and p.read_text(), where p = Path('x')
            name = node.func.attr
            candidate = literal_path(node.func.value, constants)
        if name is not None:
            if candidate is None:
                unknown.append(f"line {node.lineno}: {name}(dynamic or unsupported path)")
            else:
                dependencies.add(candidate)
    return dependencies, sorted(set(unknown))


def discover(root: Path, entries: Iterable[str]) -> dict:
    root = root.resolve()
    selected = {normalize(p) for p in entries}
    if not selected:
        raise ApprovalError("At least one entry file is required")
    seen: set[str] = set()
    pending = sorted(selected)
    unresolved: list[str] = []
    while pending:
        name = pending.pop(0)
        if name in seen:
            continue
        path = safe_file(root, name)
        seen.add(name)
        if path.suffix != '.py':
            continue
        try:
            deps, unknown = python_read_dependencies(path.read_text(encoding='utf-8'))
        except (SyntaxError, UnicodeError) as ex:
            raise ApprovalError(f"Cannot analyze Python file {name}: {ex}") from ex
        unresolved.extend(f"{name}: {issue}" for issue in unknown)
        for item in sorted(deps):
            # Scope intentionally anchored to repository root working directory
            item = normalize(item)
            if item not in seen:
                pending.append(item)
    return {'entries': sorted(selected), 'files': sorted(seen), 'unresolved': sorted(set(unresolved))}


def approve(root: Path, entries: list[str], includes: list[str], manifest: Path) -> dict:
    root = root.resolve()
    destination = manifest.resolve()
    if destination == root or root in destination.parents:
        raise ApprovalError('Manifest must be kept OUTSIDE the mutable repository root')
    scan = discover(root, entries)
    if scan['unresolved']:
        raise ApprovalError('Unresolved dynamic file reads. Refuse to approve:\n' + '\n'.join(scan['unresolved']))
    names = sorted(set(scan['files']) | {normalize(p) for p in includes})
    evidence = {name: digest(safe_file(root, name)) for name in names}
    record = {
        'schema': 'shadowinputs.approval.v1',
        'hash_algorithm': 'sha256',
        'entries': scan['entries'],
        'files': evidence,
        'limitations': 'Literal Python reads plus explicit entries/includes; does not trace imports, dynamic or external inputs',
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return record


def verify(root: Path, manifest: Path) -> tuple[bool, list[str]]:
    root = root.resolve()
    location = manifest.resolve()
    if location == root or root in location.parents:
        raise ApprovalError('Manifest must remain OUTSIDE mutable repository root')
    try:
        record = json.loads(location.read_text(encoding='utf-8'))
    except (OSError, ValueError) as ex:
        raise ApprovalError(f"Cannot read trusted approval manifest: {ex}") from ex
    if record.get('schema') != 'shadowinputs.approval.v1' or record.get('hash_algorithm') != 'sha256':
        raise ApprovalError('Unsupported approval manifest schema/algorithm')
    entries, files = record.get('entries'), record.get('files')
    if not isinstance(entries, list) or not isinstance(files, dict) or not entries or not files:
        raise ApprovalError('Malformed manifest entries/files')
    if not set(entries).issubset(files):
        raise ApprovalError('Manifest does not include its entry files')
    issues = []
    for name, expected in sorted(files.items()):
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
            raise ApprovalError(f'Invalid SHA-256 for {name}')
        try:
            actual = digest(safe_file(root, name))
        except ApprovalError as ex:
            issues.append(f"{name}: {ex}")
            continue
        if actual != expected:
            issues.append(f"{name}: CHANGED expected={expected[:12]} actual={actual[:12]}")
    return not issues, issues
