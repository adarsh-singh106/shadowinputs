"""Synthetic, non-executed training fixture. No real deployment."""
import json
from pathlib import Path

policy = json.loads(Path('policy.json').read_text(encoding='utf-8'))
print('Synthetic policy:', policy)
