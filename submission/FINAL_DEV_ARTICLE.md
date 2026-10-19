---
title: "The Deployment Script Was Approved. The File It Read Wasn't."
published: true
tags: devchallenge, hf26challenge, opensource, security
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

## What I Built

Imagine reviewing a deployment pull request at work. You inspect the GitHub Actions workflow and the Python deployment script it calls. Everything looks correct and matches policy. You click "approve".

Shortly before execution, someone changes a small configuration file in the repository that the script reads — say, `policy.json` — flipping `"require_human_review": true` to `false`. The deployment script itself was not modified. The workflow was not modified.

Did the original approval still mean the same thing?

In most CI pipelines, that approval is blind to input changes. The pipeline sees the approved script commit, passes the gate, and runs.

That problem led to **ShadowInputs**, an open-source security prototype designed to make approval depend on **the full set of files an execution reads**, not just the entrypoint script someone clicked approve on.

In our synthetic scenario:
- `deploy.py` reads `policy.json`.
- The reviewed entrypoint code stays completely unchanged.
- When `policy.json` is modified, ShadowInputs detects cryptographic drift in the dependency and emits an immediate **`BLOCK`** with a nonzero exit code (exit 1).
- When an unrelated file (like a documentation fix) changes, ShadowInputs issues a **`PASS`** (exit 0) without triggering false alarms.

The underlying failure mode is not my invention. I came across the October 2026 paper [*When the Approved File Is Unchanged: Authority-Set Integrity for Deployment and Coding-Agent Approvals*](https://arxiv.org/abs/2610.15137) by Md Imran Hossen, which formalizes this exact authority-set vulnerability in modern software delivery and agentic environments. ShadowInputs is a constrained, transparent attempt to make part of that thesis reproducible and testable on a standard developer workstation.

**Who might pay for this? (Business Hypothesis)**  
Small DevOps consultancies and teams managing sensitive release gates or regulated deployment pipelines. A commercial offering could involve audit services mapping obscure configuration dependencies, writing custom AST/runtime adapters for proprietary deployment tools, and integrating cryptographic authority-set verification into CI/CD runners. The core CLI tool remains 100% free and open-source under the MIT license. This is an unvalidated business hypothesis, not a claim of existing revenue or active commercial contracts.

---

## Demo

**Video Walkthrough:** [YOUR_VIDEO_DEMO_URL]  
*(A complete 60–90 second live screen recording script and operator checklist is available in `submission/RECORDING_STORYBOARD.md`)*

The core verification workflow runs across four deterministic conditions:

| Scenario | Actual Result | Verification Status |
|---|:---:|:---:|
| Approved inputs unchanged | `PASS` | Exit code 0 |
| Unrelated repository file modified | `PASS` | Exit code 0 |
| Approved `policy.json` modified (`require_human_review: false`), `deploy.py` unchanged | `BLOCK` | Exit code 1 |
| Approved `policy.json` deleted from repository | `BLOCK` | Exit code 1 |

### Automated Test Suite
The implementation was verified locally against Python 3.14 on Windows 11:
- **21 automated tests collected**
- **20 passed, 1 skipped** (1 symlink security test safely skipped due to Windows non-developer privilege restrictions).

![Pytest Test Suite Verification](https://raw.githubusercontent.com/adarsh-singh106/shadowinputs/main/submission/assets/01_pytest_verification.png)

### Real Local Gemma 3 Model Inspection
Rather than mocking AI responses, live model inference was executed locally using an open-weight **Gemma 3** model (`gemma3:1b`) served via **Ollama**:

```powershell
py -m shadowinputs inspect `
    --root .\examples\deployment `
    --entry .github/workflows/deploy.yml --entry deploy.py `
    --model gemma3:1b --output ai-review.json
```

**Actual Observed Result:**
```json
{
  "static": {
    "entries": [".github/workflows/deploy.yml", "deploy.py"],
    "files":   [".github/workflows/deploy.yml", "deploy.py", "policy.json"],
    "unresolved": []
  },
  "ai": {
    "status": "MODEL_RETURNED_UNTRUSTED_CANDIDATES",
    "model": "gemma3:1b",
    "candidates": [],
    "rejected": [
      "relative/path",
      "{'candidates': [{'path': 'relative/path', 'reason': \"deploy.py contains JSON\"}]}"
    ],
    "uncertainties": [],
    "warning": "Human must inspect these hints. No AI suggestion is approved automatically."
  }
}
```

*(Note on Visuals: Images below are rendered terminal output cards reproducing the exact CLI commands and console outputs from Windows 11 execution.)*

![Local Gemma 3 Model Inspection](https://raw.githubusercontent.com/adarsh-singh106/shadowinputs/main/submission/assets/02_gemma_inspection.png)

**Honest Assessment of Model Performance:**  
The model inspection executed live against local Ollama, returning status `MODEL_RETURNED_UNTRUSTED_CANDIDATES` and exit code `0`. However, its actual `candidates` list was empty. In our test fixture, the AST scanner had already discovered `policy.json` (leaving no un-indexed files), and the lightweight `gemma3:1b` model hallucinated placeholder paths (such as `"relative/path"`) from the prompt schema, which our `safe_file` validator rejected. 

A successful API response is **not** proof that a 1B parameter model can magically deduce complex deployment graphs. In fact, this real-world limitation underscores our core thesis: **AI hints must always be treated as untrusted suggestions, validated against disk bounds, and never used as authorization.** The deterministic static scanner did the actual discovery; the AI was a secondary hint mechanism.

### Pre-Deployment Verification: PASS vs BLOCK
Once approved, the manifest of input hashes is stored **outside** the mutable working directory (e.g. in protected storage or `$TEMP`). Pre-execution verification validates file bytes before release:

![PASS and BLOCK CLI Verification](https://raw.githubusercontent.com/adarsh-singh106/shadowinputs/main/submission/assets/03_pass_and_block_cli.png)

---

## Code

**GitHub Repository:** https://github.com/adarsh-singh106/shadowinputs

The codebase is organized into clean, focused modules:

- `shadowinputs/core.py`: AST parser identifying literal file read operations (`open()`, `Path.read_text()`), path normalization, directory traversal defenses, and SHA-256 manifest hashing.
- `shadowinputs/ai.py`: Loopback-only Ollama API client querying local Gemma 3 models for untrusted candidate discovery suggestions.
- `shadowinputs/cli.py`: Command-line interface implementing `inspect`, `approve`, and `verify` with strict exit codes (0 for success, 1 for drift block, 2 for syntax/safety error).
- `examples/deployment/`: Synthetic deployment pipeline fixture containing `deploy.py`, `policy.json`, and `.github/workflows/deploy.yml`.
- `tests/`: Comprehensive unit tests covering path traversal attacks, deletions, unauthorized edits, malformed manifests, and loopback boundaries.

---

## How I Built It

### The Architectural Rule: Separating Discovery from Authority

The central engineering insight behind ShadowInputs is that **probabilistic models must never hold approval authority**.

When building an integrity gate, allowing an LLM to decide what passes or fails introduces non-determinism into a security-critical boundary. If a model decides which files belong in the approval set, the authority problem has merely been shifted onto the model.

Instead, ShadowInputs enforces a clear boundary:

```
[Repository Files] 
       │
       ├──► Python AST Scanner ───────┐
       │                              ▼
       └──► Local Gemma 3 (Ollama) ──► Candidate Hints (Untrusted Advice)
                                              │
                                              ▼
                                    Human Reviewer Sign-off
                                              │
                                              ▼
                                     SHA-256 Manifest
                                (Stored outside repository)
                                              │
                                              ▼
[Pre-Release Verification] ◄── Deterministic Byte Verification (PASS / BLOCK)
```

1. **Static AST Analysis:** An initial scan extracts deterministic literal file reads (e.g., `Path('policy.json').read_text()`).
2. **Local Open-Weight AI (`gemma3:1b`):** The repository structure and detected dependencies are presented to a locally hosted Gemma 3 model over loopback (`127.0.0.1:11434`). The model suggests additional candidate files that the static scanner might have missed.
3. **Strict Validation & Human Review:** All model hints are treated as untrusted data. Non-existent files or directory traversal attempts (`../`) are filtered out. A human reviewer explicitly confirms the candidate input set.
4. **Cryptographic Manifest:** Hashes are calculated and stored in an external manifest file. If a file is touched or deleted, `shadowinputs verify` returns exit code 1 immediately.

### Safe Failure Modes
If Ollama is not running or the model cannot be reached, ShadowInputs does not fabricate a clean bill of health. It emits `NOT_EVALUATED` and exits with code 2. Similarly, if the AST scanner encounters dynamic, unresolved file paths (like `open(get_filename())`), it halts and requires explicit human inclusion.

---

## Safety, Boundaries, and Limitations

Honesty about technical boundaries is essential for any security tool:

- **Prototype Scope:** This prototype handles literal Python file reads. It does not parse complex dynamic imports, arbitrary Bash subshells, dynamic `glob()` patterns, environment variables, network endpoints, or external secrets.
- **Time-of-Check to Time-of-Use (TOCTOU):** In a production system, inputs could theoretically be swapped after verification but before execution. True production deployments require immutable artifacts or isolated container snapshots.
- **Manifest Protection:** The approval manifest must reside outside the repository. Storing the manifest inside the git tree would allow an attacker to modify the approved hash in the same commit.
- **No Production Claim:** ShadowInputs is a proof-of-concept demonstrating authority-set integrity; it is not yet an enterprise-ready admission controller.

---

## Why Open Innovation Matters

Deployment gates should never be proprietary black boxes. When an organization approves a critical release, developers and auditors must be able to inspect exactly what was checked, how dependencies were resolved, and where the boundaries lie.

By building on open-source tools—Python, local open-weight Gemma 3, and Ollama—no proprietary repository data or sensitive source code ever leaves the local machine. Everything runs on loopback. Furthermore, open licensing allows teams to inspect the AST scanner, submit test cases for tricky dependency patterns, and adapt authority-set integrity checks to other programming languages.

---

## What Surprised Me

When I started exploring this problem, my intuition was to ask an LLM to output the "final approved manifest". 

However, testing quickly revealed the core warning outlined in Hossen's paper: models are inherently probabilistic and can propose inconsistent input sets across iterations. Treating AI output as authorization introduces risk rather than reducing it.

The strongest architecture turned out to be the simplest:
**Use AI for broad, untrusted discovery. Use humans for intent and review. Use SHA-256 hashes for authority.**

---

## Prize Categories

- **Best Use of Gemma:** Demonstrated a live, loopback integration querying a local open-weight **Gemma 3** model (`gemma3:1b`) hosted on Ollama. Rather than using an LLM as an unearned authority, we explored Gemma as an untrusted candidate dependency advisor alongside static AST analysis, bound its output to strict repository path validation (`safe_file`), and documented the empirical limits of lightweight local models in automated dependency discovery.
