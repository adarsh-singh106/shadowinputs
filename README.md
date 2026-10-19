# ShadowInputs 👁️

**A reviewed deployment file can be unchanged while the files it reads have changed.** ShadowInputs is a small experimental CLI that uses a **local open-weight model** to *suggest* missing input dependencies, then uses deterministic SHA-256 checks to invalidate an approval when a reviewed input changes.

> ⚠️ **Security research prototype, not a production approval system.** It recognizes a narrow subset of Python file reads and needs explicit human review of its input list. It does not discover all execution dependencies or establish adversarially secure approvals.

## What does it actually solve?

A developer approves `deploy.py`, which reads `policy.json`. Later, somebody changes `policy.json` from `"require_human_review": true` to `false`, leaving `deploy.py` untouched. Checking only `deploy.py` misses the change. ShadowInputs binds a human-approved *set of input files* to their hashes. Verification rejects drift in **any approved input**.

The issue is motivated by [When the Approved File Is Unchanged: Authority-Set Integrity for Deployment and Coding-Agent Approvals](https://arxiv.org/abs/2610.15137) (Md Imran Hossen, October 2026). The paper's problem statement is prior art; this project is a small educational implementation, not a new security discovery.

## How it works

1. **Inspect:** a tiny AST-based Python scanner identifies simple literal `open(...)` / `Path(...).read_text()` dependencies. A locally hosted **Gemma 3 model via Ollama** is asked to suggest files the scanner could have missed. Its output is **untrusted advice**, never silently added to an approved manifest.
2. **Approve:** after inspecting the static results and AI hints, a human lists entry files and any additional dependencies. ShadowInputs saves SHA-256 hashes to a JSON manifest **outside the mutable repository**, where it must be protected by the deployment operator.
3. **Verify:** immediately before an intended deployment (the prototype does *not* execute one), compare every listed file to its approved hash. Changed or missing files cause a nonzero exit code. Unrelated files are ignored.

The model is valuable for **candidate discovery**, not for comparing hashes or granting authorization. When the model is missing, `inspect` returns `NOT_EVALUATED` and exit code `2` instead of pretending a successful AI review.

## Requirements

- Python 3.10+ (tested here on Python 3.13)
- For **real AI-assisted inspection**: [Ollama](https://ollama.com/) with the `gemma3:4b` model. The model may take a while to download. The core approval checks have no network dependency.
- `pytest` for tests (optional when only running CLI)

### Setup: Windows PowerShell

```powershell
# Unzip and open the project folder
cd shadowinputs

# Optional package install (not required for module execution)
py -m pip install -e ".[dev]"

# In another terminal, make sure Ollama is running
ollama pull gemma3:4b
# If Ollama is not already running: ollama serve
```

### Run the AI inspection (do this first for contest evidence)

```powershell
py -m shadowinputs inspect --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --model gemma3:4b --output ai-review.json
```

Check the generated report. A successful *local model request* returns `MODEL_RETURNED_UNTRUSTED_CANDIDATES`. It does **not** mean every dependency was found. Missing Ollama or an invalid response is explicitly reported as `NOT_EVALUATED`.

### Approve the known synthetic inputs

Keep the manifest **outside** the folder being protected:

```powershell
py -m shadowinputs approve --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --manifest "$env:TEMP\shadowinputs-approval.json"
```

The scanner currently discovers `policy.json` through `deploy.py`. If your inspection identifies another input, first **manually verify it**, then pass `--include relative/file` when approving.

### Verify before a simulated release

```powershell
py -m shadowinputs verify --root .\examples\deployment --manifest "$env:TEMP\shadowinputs-approval.json"
```

Now edit `examples/deployment/policy.json`, changing `"require_human_review": true` to `false`, then run `verify` again. It should print `BLOCK` and exit `1`. Restore the file afterwards.

### Automatic disposable demo + tests

```powershell
py -m demo.run_demo
py -m pytest -q
```

`demo.run_demo` copies the example into a temporary directory, so it does **not** modify your working example. It demonstrates PASS on unchanged state, PASS on an unrelated edit, BLOCK on an approved policy edit, and BLOCK on deletion. The disposable demo does **not** call Gemma. Run `inspect` separately to demonstrate actual local AI use.

The same commands work on Linux/macOS if you replace `py` with `python` and use POSIX paths for `--root` / `--manifest`.

## CLI status / exit codes

| Command | Exit | Meaning |
|---|---:|---|
| `inspect` | 0 | Static scan completed, local model returned parseable candidates, no recognized unresolved reads |
| `inspect` | 2 | AI unavailable or static scan unresolved; review incomplete |
| `approve` | 0 | Manifest saved after human-selected scope |
| `approve` | 2 | Unsafe input, unsupported unresolved read, missing file, or invalid manifest path |
| `verify` | 0 | All listed file bytes match the manifest |
| `verify` | 1 | At least one listed file is changed or missing |
| `verify` | 2 | Manifest or path verification error |

## Safety and limitations (read before relying on this)

- **Not complete input discovery.** The AST scanner recognizes basic literal Python `open` and `Path.read_text`/`read_bytes`/`open`; it does not trace imported modules, shells, GitHub Actions YAML semantics, `glob`, network APIs, runtime-generated paths, environment variables, symlink changes after verification, toolchains, packages, or external secrets. It analyzes Python source but does not execute it.
- **TOCTOU:** there is a time-of-check-to-time-of-use race if inputs change between verifying and executing. In production, use immutable artifacts/snapshots and trusted execution context.
- **Trust boundary:** the approval manifest must be genuinely secured outside the mutable checkout. Merely keeping it in a parent directory does **not** secure it if the attacker can edit that parent. We do not sign manifests or provide reviewer identity authentication.
- **Model limitations:** candidate suggestions can be inaccurate or incomplete. Model output is untrusted repository data. There are no accuracy benchmarks in this prototype.
- **Absolute paths and symlinks:** intentionally unsupported, fail with an error. The model is configured to communicate only with an Ollama instance on loopback.
- **Not GitHub enforcement:** this prototype does not install a GitHub Action, integrate with protected environments, or execute a release. Integrations need additional hardening before real deployment use.
- **No unverified business claims:** No paying user or completed security audit has been documented.

## Why open source and who might pay?

The tool and manifest are MIT-licensed; teams can inspect the checks, run the model on their own machines, and contribute safer analyzers for additional languages or workflow formats. Private repositories never need to be sent to a third-party model API. Commercialization hypothesis: a specialist integrator could charge for mapping high-risk deployment inputs, reviewing approvals, and maintaining validated CI adapters. **These are hypotheses, not measured willingness-to-pay.**

## Project layout

```text
shadowinputs/
  shadowinputs/{core.py,ai.py,cli.py}
  examples/deployment/{deploy.py,policy.json,.github/workflows/deploy.yml}
  tests/{test_core.py,test_ai.py}
  demo/run_demo.py
  docs/{DEV_ARTICLE_DRAFT.md,SUBMISSION_CHECKLIST.md}
```

## Contributing and credit

- License: MIT (`LICENSE`)
- Contributions: see `CONTRIBUTING.md`
- Research credit: [Hossen, *When the Approved File Is Unchanged*](https://arxiv.org/abs/2610.15137).
- Existing tools such as GitHub branch protections, CodeQL and policy-as-code engines serve related but different purposes. This project doesn't claim to replace them.
