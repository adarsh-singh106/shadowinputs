"""An actual, deterministic, non-AI demonstration with disposable files."""
import shutil
import tempfile
from pathlib import Path

from shadowinputs.core import approve, verify


def run():
    source = Path(__file__).resolve().parents[1] / 'examples' / 'deployment'
    with tempfile.TemporaryDirectory(prefix='shadowinputs-') as temp:
        base = Path(temp)
        root = base / 'repo'
        shutil.copytree(source, root)
        manifest = base / 'approval.json'
        entries = ['.github/workflows/deploy.yml', 'deploy.py']
        print('SCENARIO: A reviewed workflow calls deploy.py, which reads policy.json.')
        record = approve(root, entries, [], manifest)
        print('Approved:', ', '.join(record['files']))
        assert 'policy.json' in record['files']
        clean, _ = verify(root, manifest)
        print('1) Nothing changed      ', 'PASS' if clean else 'FAIL')
        assert clean
        (root / 'README.txt').write_text('Unrelated documentation change')
        unrelated, _ = verify(root, manifest)
        print('2) Unrelated file edit  ', 'PASS' if unrelated else 'FAIL')
        assert unrelated
        policy = root / 'policy.json'
        policy.write_text(policy.read_text().replace('true', 'false'))
        changed, issues = verify(root, manifest)
        print('3) Policy changed       ', 'BLOCK' if not changed else 'FAIL')
        for issue in issues:
            print('    Evidence:', issue)
        assert not changed
        policy.unlink()
        missing, _ = verify(root, manifest)
        print('4) Policy removed       ', 'BLOCK' if not missing else 'FAIL')
        assert not missing
        print('ALL DETERMINISTIC SCENARIOS VERIFIED. Local model not invoked in this demo.')


if __name__ == '__main__':
    run()
