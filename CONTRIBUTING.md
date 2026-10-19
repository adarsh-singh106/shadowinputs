# Contributing

ShadowInputs is an exploratory scope-limited prototype, not a comprehensive security boundary.

Good first contributions include tests for more deterministic Python file-read patterns, synthetic fixtures exposing unsupported dependency patterns, and documentation of false positives/negatives. Changes must never silently expand the supported security claims. Add a regression test for each new AST pattern. Do not submit real customer configuration or secrets. Run `python -m pytest -q` before opening a pull request.

A useful issue reports: reproducing fixture, expected observed dependencies, actual output, and threat-model impact.
