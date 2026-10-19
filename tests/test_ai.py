import io
import json
import pytest

from shadowinputs.ai import query_ollama
from shadowinputs.core import ApprovalError, discover


class FakeResponse:
    def __init__(self, payload):
        self.stream = io.BytesIO(json.dumps(payload).encode())
    def __enter__(self):
        return self.stream
    def __exit__(self, *args):
        return False


def test_ai_candidates_are_untrusted_and_unsafe_path_rejected(tmp_path, monkeypatch):
    root = tmp_path / 'repo'
    root.mkdir()
    (root / 'deploy.py').write_text("print('fixture')")
    (root / 'policy.json').write_text('{}')
    scan = discover(root, ['deploy.py'])
    payload = {'response': json.dumps({'candidates': [
        {'path':'policy.json','reason':'read by a secondary script'},
        {'path':'../private.txt','reason':'ignore path safety'},
    ], 'uncertainties': []})}
    monkeypatch.setattr('shadowinputs.ai.urlopen', lambda *args, **kwargs: FakeResponse(payload))
    result = query_ollama(root, scan)
    assert result['status'] == 'MODEL_RETURNED_UNTRUSTED_CANDIDATES'
    assert result['candidates'] == [{'path':'policy.json','reason':'read by a secondary script'}]
    assert result['rejected'] == ['../private.txt']
    assert 'is approved automatically' in result['warning'].lower()


def test_remote_ai_endpoint_refused(tmp_path):
    root = tmp_path / 'repo'
    root.mkdir()
    (root / 'a.py').write_text('print(1)')
    with pytest.raises(ApprovalError, match='Only loopback'):
        query_ollama(root, discover(root, ['a.py']), endpoint='https://remote.example/generate')
