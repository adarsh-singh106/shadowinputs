---
title: "The Deployment Script Was Approved. The File It Read Wasn't."
published: true
tags: devchallenge, hf26challenge, opensource, security
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).* 

## What I Built

Imagine approving a deployment script after reading every line. The script stays unchanged, but before the deployment somebody edits a JSON file that the script reads:

```diff
- "require_human_review": true
+ "require_human_review": false
```

If your approval check watches only the script, it can miss a behavior-changing edit to an input. **The approved file hasn't changed, but the approved behavior might have.**

This is the problem I explored with **ShadowInputs**, a small open-source Python CLI that records the hashes of a **reviewed set of repository-local files** and reports when those file contents change before a simulated deployment. It is a prototype, not an automatic safeguard for every CI/CD system.

The idea was inspired by Md Imran Hossen's October 2026 paper, [*When the Approved File Is Unchanged: Authority-Set Integrity for Deployment and Coding-Agent Approvals*](https://arxiv.org/abs/2610.15137). The paper highlights why an approval attached to one file may not cover all the inputs that determine execution behavior. I built a constrained implementation to investigate the idea on a developer laptop, rather than claim to solve the entire research problem.

### Who would pay for it?

**Business hypothesis, not validated revenue:** Small DevOps consultancies or teams operating sensitive release gates might pay for **dependency-mapping audits, adapters for their specific deployment tools, and CI integration**. The CLI and example checks remain free under the MIT license. A production paid service would first need real customer interviews, a broader dependency model, and a proper authorization/integrity design.

## Demo

**Video walkthrough:** [Watch 74-Second Demo Walkthrough](https://github.com/adarsh-singh106/shadowinputs/blob/main/submission/assets/shadowinputs_demo_walkthrough.mp4) *(Included in repository: [`shadowinputs_demo_walkthrough.mp4`](https://raw.githubusercontent.com/adarsh-singh106/shadowinputs/main/submission/assets/shadowinputs_demo_walkthrough.mp4))*

The demonstration uses a synthetic GitHub Actions workflow, a Python `deploy.py` script, and a `policy.json` input. The workflow and entrypoint are explicitly supplied to the CLI; the prototype does **not** fully parse GitHub Actions or discover every runtime dependency.

| Scenario | Observed CLI result | Exit code |
| --- | --- | --- |
| Approved files unchanged | `PASS` | `0` |
| Unrelated documentation edit | `PASS` | `0` |
| Approved `policy.json` changed, `deploy.py` unchanged | `BLOCK` | `1` |
| Approved `policy.json` deleted | `BLOCK` | `1` |

The Windows 11 / Python 3.14 agent run reported **20 tests passed, 1 skipped**. The skipped test checks symlink handling, which required a Windows privilege unavailable in that environment. These tests demonstrate a limited CLI behavior, **not production security assurance**.

![Pytest output shown in a rendered terminal card](https://raw.githubusercontent.com/adarsh-singh106/shadowinputs/main/submission/assets/01_pytest_verification.png)

### What happened with real Gemma inference?

I also ran a local **Gemma 3 1B** model through **Ollama** to suggest possible file dependencies that a static scanner might miss. The test run was real, not a mocked model answer:

```powershell
py -m shadowinputs inspect `
  --root .\examples\deployment `
  --entry .github/workflows/deploy.yml `
  --entry deploy.py `
  --model gemma3:1b `
  --output ai-review.json
```

The static scanner found `deploy.py`, the workflow entry and `policy.json`. The model returned **zero accepted additional candidates** and suggested a placeholder path (`relative/path`), which the path validator rejected. The model call succeeded, but it **did not improve dependency coverage in this experiment**.

That disappointing result was useful engineering feedback. A successful model response is not evidence of successful dependency discovery. In an integrity tool, the model must remain a *source of untrusted hints*, never the authority that decides whether deployment can proceed.

![Rendered terminal card reproducing the Gemma inspection output](https://raw.githubusercontent.com/adarsh-singh106/shadowinputs/main/submission/assets/02_gemma_inspection.png)

![Rendered terminal card reproducing PASS and BLOCK CLI output](https://raw.githubusercontent.com/adarsh-singh106/shadowinputs/main/submission/assets/03_pass_and_block_cli.png)

*Image note: These cards were generated from reported terminal output, not captured as unedited desktop screenshots. The linked live video should show the actual commands and their outputs.*

## Code

**Repository:** [ShadowInputs on GitHub](https://github.com/adarsh-singh106/shadowinputs)

The core pieces are deliberately small:

- `shadowinputs/core.py`: scoped Python AST checks for common literal file reads, path validation, SHA-256 hashing and manifest comparison.
- `shadowinputs/ai.py`: a loopback-only Ollama request to Gemma for additional *untrusted* candidate paths.
- `shadowinputs/cli.py`: `inspect`, `approve`, and `verify` commands with machine-readable exit codes.
- `examples/deployment/`: a synthetic fixture that makes the changed-input failure easy to reproduce.
- `tests/`: regression tests for drift, missing files, unsupported paths and other known boundaries.

Here is the basic workflow (from the project root):

```powershell
py -m shadowinputs approve `
  --root .\examples\deployment `
  --entry .github/workflows/deploy.yml `
  --entry deploy.py `
  --manifest "$env:TEMP\shadowinputs-approved.json"

py -m shadowinputs verify `
  --root .\examples\deployment `
  --manifest "$env:TEMP\shadowinputs-approved.json"
```

`approve` records a manifest **after the operator has reviewed the scope**. It does not currently authenticate that reviewer or cryptographically sign their decision; the manifest must be protected by a trusted external process. If a listed file's bytes change or the file disappears, `verify` returns a failure instead of silently continuing.

## How I Built It

The design separates **suggestion**, **review**, and **verification**:

1. **Explicit scope + static scan.** I provide the entry files. A Python AST scanner discovers some common literal file reads such as `Path('policy.json').read_text()`. It flags some unresolved dynamic reads rather than pretending it knows every dependency.
2. **Local Gemma hints.** Ollama runs Gemma locally to propose *possible* additional repository paths. Those suggestions are not automatically included in the trusted set and are checked against the filesystem. The initial experiment yielded no accepted additional hints.
3. **Operator-reviewed manifest.** The CLI records SHA-256 digests of the discovered and explicitly included files. This is a hash snapshot, **not a signed human approval system**.
4. **Deterministic drift check.** Before simulated execution, the CLI compares the manifest with current file bytes. For the listed files, drift is a reason to block. It doesn't change or execute the actual deployment.

The most important lesson was that an LLM belongs on the *discovery side* of the boundary, not the *authorization side*. I want a reviewer to be able to inspect every accepted path and reproduce the check without trusting an opaque model score.

### What this prototype cannot guarantee

- It does **not** discover the complete file set used by arbitrary Python, shell, GitHub Actions or deployment tools. Imports, environment variables, dynamic paths and external services remain out of scope.
- Files that were never included in the manifest are **not protected**. A `PASS` means only that *manifest-listed bytes* matched.
- Keeping the manifest outside the repository is necessary for this demo, but **location alone doesn't make it tamper-proof**; a real gate would need protected storage and access controls.
- It does not protect against files being replaced **after verification** (time-of-check to time-of-use). Immutable artifacts or isolated execution would be required.
- An operator can run `approve`; no independent reviewer identity or authorization is enforced in this version.
- Gemma's initial real run found **no additional useful dependencies**. That is a measured limitation, not a feature success.

## Why Open Innovation Matters

I chose a local open-weight model and an inspectable Python CLI because deployment source code can be sensitive, and because a security-related tool should be auditable. The prototype sends model requests to an Ollama endpoint restricted to loopback instead of depending on a hosted model API. That makes it possible to test the workflow on a developer machine without sending repository snippets to a cloud inference provider.

The biggest open-source value is not the chatbot-style interface. It's the **reproducible test case and extensible input-discovery tooling**: another developer can inspect the hash calculation, reproduce the failing scenario, contribute a parser for another deployment language, or add an edge case that makes the next release safer. The limitations are visible in code rather than hidden behind a vendor's approval decision.

## What I'd Test Next

The next meaningful experiment is not a larger dashboard. It's a corpus of real deployment patterns where the static scanner misses an input, followed by a controlled comparison: **static scanner alone vs. static scanner plus Gemma suggestions, with precision, recall, and time measured**. Until that evidence exists, I won't claim AI improves coverage.

## Prize Categories

- **Best Use of Gemma:** ShadowInputs integrates a locally run Gemma 3 model using Ollama for candidate dependency suggestions. I documented its actual zero-additional-candidate result and validated model output as untrusted data. This is a working model integration, though the initial run does not establish a performance improvement.
