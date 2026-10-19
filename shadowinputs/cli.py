"""shadowinputs: local approval drift checks for a deliberately narrow file scope."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import ApprovalError, approve, discover, verify
from .ai import query_ollama


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='shadowinputs', description='Review inputs, approve their hashes, detect drift before execution.')
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'approve', 'verify'):
        c = sub.add_parser(name)
        c.add_argument('--root', type=Path, required=True, help='Repository root / working directory')
        if name in ('inspect', 'approve'):
            c.add_argument('--entry', action='append', required=True, help='Explicit entry file; repeat for workflow and Python entrypoint')
        if name == 'inspect':
            c.add_argument('--model', default='gemma3:4b')
            c.add_argument('--no-ai', action='store_true', help='Scanner only (not a full open-AI demo)')
            c.add_argument('--output', type=Path, help='Optional saved JSON inspection report')
        elif name == 'approve':
            c.add_argument('--include', action='append', default=[], help='Human-reviewed extra input; repeat as needed')
            c.add_argument('--manifest', type=Path, required=True, help='Outside-repository approval file')
        else:
            c.add_argument('--manifest', type=Path, required=True, help='Trusted approved manifest outside repository')
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == 'inspect':
            report = {'static': discover(args.root, args.entry)}
            if args.no_ai:
                report['ai'] = {'status': 'NOT_EVALUATED', 'reason': '--no-ai requested'}
            else:
                try:
                    report['ai'] = query_ollama(args.root, report['static'], args.model)
                except ApprovalError as ex:
                    report['ai'] = {'status': 'NOT_EVALUATED', 'reason': str(ex)}
            result = json.dumps(report, indent=2, ensure_ascii=False)
            print(result)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(result + '\n', encoding='utf-8')
            return 0 if not report['static']['unresolved'] and report['ai']['status'] == 'MODEL_RETURNED_UNTRUSTED_CANDIDATES' else 2
        if args.command == 'approve':
            manifest = approve(args.root, args.entry, args.include, args.manifest)
            print(f"APPROVED: {len(manifest['files'])} files. Manifest: {args.manifest}")
            print('Only approve after reviewing all inputs and the AI inspection report.')
            return 0
        good, issues = verify(args.root, args.manifest)
        if good:
            print('PASS: All approved repository-local input digests match.')
            return 0
        print('BLOCK: Approved input state has changed:')
        for issue in issues:
            print(' -', issue)
        return 1
    except ApprovalError as ex:
        print(f'ERROR: {ex}')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
