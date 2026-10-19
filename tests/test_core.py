import json
from pathlib import Path

import pytest

from shadowinputs.core import (
    ApprovalError, approve, discover, normalize, python_read_dependencies,
    safe_file, verify,
)
from shadowinputs.cli import main


def make_fixture(tmp_path):
    root = tmp_path / 'repo'
    root.mkdir()
    (root / 'deploy.py').write_text("from pathlib import Path\nPath('policy.json').read_text()\n", encoding='utf-8')
    (root / 'policy.json').write_text('{"review":true}', encoding='utf-8')
    return root, tmp_path / 'protected-approval.json'


def test_detects_literal_path_read(tmp_path):
    root, _ = make_fixture(tmp_path)
    scan = discover(root, ['deploy.py'])
    assert scan['files'] == ['deploy.py', 'policy.json']
    assert scan['unresolved'] == []


def test_approved_and_unchanged_passes(tmp_path):
    root, manifest = make_fixture(tmp_path)
    approve(root, ['deploy.py'], [], manifest)
    assert verify(root, manifest) == (True, [])


def test_changed_dependency_blocks_without_entry_change(tmp_path):
    root, manifest = make_fixture(tmp_path)
    entry = (root / 'deploy.py').read_bytes()
    approve(root, ['deploy.py'], [], manifest)
    (root / 'policy.json').write_text('{"review":false}')
    okay, issues = verify(root, manifest)
    assert not okay and 'policy.json: CHANGED' in issues[0]
    assert (root / 'deploy.py').read_bytes() == entry


def test_missing_dependency_blocks(tmp_path):
    root, manifest = make_fixture(tmp_path)
    approve(root, ['deploy.py'], [], manifest)
    (root / 'policy.json').unlink()
    okay, issues = verify(root, manifest)
    assert not okay and 'policy.json' in issues[0]


def test_unrelated_file_edit_does_not_block(tmp_path):
    root, manifest = make_fixture(tmp_path)
    approve(root, ['deploy.py'], [], manifest)
    (root / 'readme.txt').write_text('unrelated file')
    assert verify(root, manifest) == (True, [])


def test_changing_entry_blocks(tmp_path):
    root, manifest = make_fixture(tmp_path)
    approve(root, ['deploy.py'], [], manifest)
    (root / 'deploy.py').write_text('print("changed")')
    assert verify(root, manifest)[0] is False


@pytest.mark.parametrize('value', ['../oops.txt', '/tmp/absolute', 'x\\y.txt', 'a//b', './a', 'C:/windows.txt'])
def test_unsafe_paths_rejected(value):
    with pytest.raises(ApprovalError):
        normalize(value)


def test_symlink_outside_repo_rejected(tmp_path):
    root, _ = make_fixture(tmp_path)
    outside = tmp_path / 'secret.json'
    outside.write_text('{}')
    link = root / 'link.json'
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip('System does not allow symlinks')
    with pytest.raises(ApprovalError):
        safe_file(root, 'link.json')


def test_manifest_inside_root_rejected(tmp_path):
    root, _ = make_fixture(tmp_path)
    with pytest.raises(ApprovalError, match='OUTSIDE'):
        approve(root, ['deploy.py'], [], root / 'approval.json')


def test_unresolved_reads_fail_closed(tmp_path):
    root, manifest = make_fixture(tmp_path)
    (root / 'deploy.py').write_text('filename = get_path()\nopen(filename).read()')
    scan = discover(root, ['deploy.py'])
    assert scan['unresolved']
    with pytest.raises(ApprovalError, match='Unresolved'):
        approve(root, ['deploy.py'], [], manifest)


def test_read_variable_bound_to_literal():
    files, missing = python_read_dependencies('from pathlib import Path\np = Path("config.json")\np.read_text()')
    assert files == {'config.json'} and missing == []


def test_explicit_extra_is_protected(tmp_path):
    root, manifest = make_fixture(tmp_path)
    (root / 'extra.ini').write_text('mode=old')
    approve(root, ['deploy.py'], ['extra.ini'], manifest)
    (root / 'extra.ini').write_text('mode=new')
    assert verify(root, manifest)[0] is False


def test_cli_inspect_without_model_reports_unverified(tmp_path, capsys):
    root, _ = make_fixture(tmp_path)
    code = main(['inspect', '--root', str(root), '--entry', 'deploy.py', '--no-ai'])
    captured = capsys.readouterr().out
    assert code == 2
    assert 'NOT_EVALUATED' in captured


def test_refuses_malformed_manifest(tmp_path):
    root, manifest = make_fixture(tmp_path)
    manifest.write_text(json.dumps({'schema':'wrong'}))
    with pytest.raises(ApprovalError, match='Unsupported'):
        verify(root, manifest)
