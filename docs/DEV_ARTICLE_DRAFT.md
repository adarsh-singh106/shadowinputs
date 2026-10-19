---
title: "The Deployment Script Was Approved. The File It Read Wasn't."
published: false
tags: devchallenge, hf26challenge, opensource, security
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

> **Before publishing:** Replace `[YOUR_GITHUB_REPO_URL]` and `[YOUR_VIDEO_DEMO_URL]`, run the local Gemma `inspect` command, and update the explicitly unverified AI evidence below. Do not publish unresolved placeholders or pretend model inference happened if it didn't.

## What I Built

Imagine approving a deployment at work. You inspect the workflow and the script it calls. Everything looks fine. Then somebody changes one configuration file that the script reads, without touching the approved script.

Did the approval still mean the same thing?

That question led me to **ShadowInputs**, a small open-source prototype that makes approval depend on **the files a run reads**, not just the file someone clicked “approve” on.

In my synthetic example, `deploy.py` reads `policy.json`. The reviewed code stays unchanged, but the configuration changes from `"require_human_review": true` to `false`. ShadowInputs catches the drift and blocks a *simulated* deployment by returning a nonzero exit code. It does not execute or secure a real release pipeline yet.

The underlying problem is not my discovery. I came across the October 2026 paper [*When the Approved File Is Unchanged: Authority-Set Integrity for Deployment and Coding-Agent Approvals*](https://arxiv.org/abs/2610.15137), which studies this failure mode in public projects. My project is a constrained attempt to make part of that idea reproducible on a laptop.

**Who might pay?** Small DevOps consultancies and teams working on sensitive release pipelines. I could imagine paid work mapping configuration dependencies, integrating checks with CI, and performing review-led deployment audits. The CLI stays free. This is a **business hypothesis**, not a statement that I have a customer or validated pricing.

## Demo

**Video:** [YOUR_VIDEO_DEMO_URL]

The first part is a disposable local scenario. It tests four conditions:

| Scenario | Actual result |
|---|---|
| Approved inputs unchanged | `PASS` |
| An unrelated file changed | `PASS` |
| Approved `policy.json` changed, `deploy.py` unchanged | `BLOCK` |
| Approved `policy.json` deleted | `BLOCK` |

I ran the full test suite in the development environment: **21 automated tests passed** on Python 3.13. These results verify the deterministic prototype, not its completeness as a security product.

**Local AI inspection evidence:** [REPLACE WITH THE REAL RESULT OF RUNNING `inspect` WITH GEMMA ON YOUR MACHINE; otherwise explicitly state that model integration was implemented and mocked in tests but live inference was not verified].

The model inspection stage is crucial to this concept: it suggests dependencies a narrow static scanner might miss. The human reviewer must still validate each suggestion. The model isn't allowed to issue approvals or change manifest contents on its own.

## Code

**Repository:** [YOUR_GITHUB_REPO_URL]

The implementation has three small components: 

- `shadowinputs/core.py`: limited Python AST discovery, safe path checks, and file hashing.
- `shadowinputs/ai.py`: local Gemma/Ollama calls for **untrusted dependency candidate suggestions**.
- `shadowinputs/cli.py`: `inspect`, `approve`, and `verify` commands with clear exit codes.

For reproducibility, `python -m demo.run_demo` copies the sample into a temporary directory and demonstrates the same four decisions without modifying the checked-in fixture. `python -m pytest -q` runs unit tests covering changes, deletions, path traversal, symlinks, incomplete inspections, and malformed manifests.

## How I Built It

One design decision mattered more than the model choice: **separating discovery from authority**.

I use an AST scanner to recognize simple Python file reads such as `Path('policy.json').read_text()`. I then provide the selected source files, discovered paths, and repository file listing to a **Gemma 3 open-weight model through locally hosted Ollama**. The model proposes additional candidate paths and reasons. Nothing it says is treated as an approval.

After reviewing the dependency list, a human records the selected input file paths and SHA-256 hashes in a manifest **stored outside the mutable project directory**. A verification command compares all approved file contents against that manifest before an intended release. Changed or missing files cause failure. An unrelated file doesn't invalidate the approval.

This separation avoids using a probabilistic model as the final authority on a deterministic question. The AI helps discover candidate input relationships; ordinary code verifies the bytes.

I explicitly stop if the static scanner encounters supported-looking but unresolved dynamic file reads. And if Ollama isn't available, the AI inspection says `NOT_EVALUATED`, rather than presenting a fake successful review.

There are big caveats. This prototype doesn't parse all CI workflows, follow arbitrary imports, capture network dependencies, prevent a time-of-check/time-of-use race, sign manifests, or enforce real production releases. The example is intentionally narrow. I think showing that boundary is more valuable than calling this “enterprise-grade security” after one afternoon.

## Why Does Open Innovation Matter?

A dependency approval mechanism should be inspectable. A team must know what was checked, which files were included, and what got ignored. That's hard to reason about when the important part is a proprietary black box.

Here the CLI and manifest format are published under MIT. The AI inspection can run locally on a developer's machine. There's no requirement to upload private deployment code to someone else's API. Future contributors could add language adapters, safe parsers for workflow formats, or test fixtures that demonstrate false negatives.

Open source matters especially because **the input set is the security-sensitive decision**. If different teams discover blind spots, everyone should be able to improve the verifier and share reproducible regression cases.

## What Surprised Me

My first instinct was to ask the AI to tell me the full file dependency set. But the source research cautions that models can choose inconsistent input sets. If the model decides which files are checked and we trust it, we've just moved the approval problem to the model.

So I ended up with a less flashy design: AI suggests, humans review, hashes decide. It is incomplete, and it is honest about being incomplete.

The most useful next experiment isn't adding more features. It's constructing adversarial fixtures where a Python script depends on files through imports or indirect reads, then measuring which inputs the static scanner misses and whether local Gemma provides additional useful candidates.

## My Agent Session

This development used AI-assisted coding and review. [OPTIONAL: Add an actual DevRelay/agent-session URL, if you have one. Otherwise remove this section.]

## Prize Categories

- **Best Use of Gemma:** [KEEP ONLY AFTER YOU HAVE RUN AND EVIDENCED REAL GEMMA INFERENCE LOCALLY. Otherwise remove this line and section.]

> No claim of a paying user, deployed production security system, or measured model accuracy is made.
