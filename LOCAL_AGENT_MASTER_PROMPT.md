# ShadowInputs: Local Agent Master Prompt

You are my senior Python engineer, QA lead, demo producer, and DEV submission editor. We have an urgent submission deadline on October 19, 2026, at 12:29 PM IST. Execute efficiently, do not overengineer, and be factual about every result.

## Context and objective

This is a **brand-new standalone** open-source Hacktoberfest 2026 Week 2 Side Hustle entry named **ShadowInputs**. The source code is already present in this directory. **Do not rebuild it from scratch** or switch project ideas. Its core claim is narrow: if a reviewed deployment entrypoint remains unchanged but a reviewed repository-local input (e.g. `policy.json`) changes, a pre-execution hash check identifies stale approval and emits a nonzero result.

Open-source AI is used for *candidate dependency discovery* via local Gemma/Ollama. Gemma is not trusted to approve input sets; deterministic validation checks the selected file bytes. This is NOT a production-grade release security system. Potential customers are DevOps consultants requiring deployment-integrity audit/integration services, which is an **unvalidated** commercial hypothesis.

Read `README.md`, `docs/SUBMISSION_CHECKLIST.md`, `docs/DEV_ARTICLE_DRAFT.md`, `pyproject.toml`, CLI source, fixture files and tests before changing anything. Only work inside this `shadowinputs/` directory. Preserve original code unless correcting a demonstrated blocker. No unrelated tools, no large features, no website or database.

## Priority 1: Verify actual runnable software

1. Inspect the existing repository and its setup on Windows PowerShell; state any issues.
2. Run `py -m pip install -e ".[dev]"` only if dependencies need installation (use existing environment if ready). Run `py -m pytest -q` and `py -m demo.run_demo`. Preserve exact actual output in `evidence/` as UTF-8 text; no invented successes. `demo.run_demo` uses disposable fixtures.
3. Confirm baseline `PASS`, unrelated change `PASS`, policy modification `BLOCK`, policy deletion `BLOCK`, and test count. If anything fails, investigate and apply the smallest safe fix, then rerun tests.
4. The project is safe to demo: **never execute real deployment commands**. Do not claim production protection.

## Priority 2: Run REAL Gemma inference, no mocks

1. Check `ollama --version`, running Ollama service, `ollama list` and the installed models.
2. Preferred model `gemma3:4b` (as existing README suggests); if not installed, evaluate download time/network/disk and ask before any large install. If deadline pressure makes 4b impractical, use a smaller **real compatible Gemma model** such as `gemma3:1b` and accurately update commands/article to name the actually used model. Do not claim one model when another was run.
3. Run the real command from project root:

```powershell
py -m shadowinputs inspect --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --model gemma3:4b --output ai-review.json
```

4. Check actual output and exit code, including `MODEL_RETURNED_UNTRUSTED_CANDIDATES` versus `NOT_EVALUATED`, and save redacted evidence to `evidence/`. Manually verify AI-suggested paths against the fixture. Do NOT pretend mocked AI test results are a real model run. If Ollama fails, disclose failure and proceed with verified deterministic results.
5. Demonstrate manual approval and validation commands, keeping manifest outside protected repo:

```powershell
py -m shadowinputs approve --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --manifest "$env:TEMP\shadowinputs-approval.json"
py -m shadowinputs verify --root .\examples\deployment --manifest "$env:TEMP\shadowinputs-approval.json"
```

Use the disposable demo to show drift without altering working files, or if manually editing fixture make certain to restore it and rerun tests.

## Priority 3: Authentic visual evidence

Produce **at least three readable, real screenshots** in `submission/assets/`:
- actual terminal `py -m pytest -q` showing outcome;
- actual local Gemma inspection response (if successfully run; if not, show `NOT_EVALUATED` explicitly);
- actual CLI demonstration of `PASS` and `BLOCK` with relevant file names, preferably alongside edited `policy.json`.

Use Windows Snipping Tool, built-in recording, OBS, or available screenshot tools. If automated desktop capture is impossible, give me exact commands/keystrokes to capture manually and do not fabricate screenshot files. Crop secrets or local personal paths and confirm text is legible. Existing `demo/actual_cli_output.png` is a graphic of real deterministic outputs, **not** evidence of Gemma execution; label it accurately if used.

Record a **60 to 90 second authentic screen-capture demonstration** in `submission/assets/` if your environment supports real screen recording. Suggested order:
- 0–12s: Explain `deploy.py` reads `policy.json` while approved script remains unchanged.
- 12–30s: Run real Ollama `inspect`; show precise AI status, no mock.
- 30–45s: Show successful approval/verify.
- 45–65s: Show a modified approved policy causing BLOCK, nonzero exit status.
- 65–85s: Show passing pytest tests, GitHub repo, limitations.

If real screen capture is unavailable, make a precise **recording storyboard and operator checklist** instead, and let me record it manually. Never call a reconstructed/static video a live screen recording. Existing `demo/shadowinputs_static_demo.mp4` lasts 27 seconds and shows deterministic CLI output only; it is a possible fallback, not proof of live Gemma inference. Don't simulate a model terminal screen or make false claims.

## Priority 4: Repository and DEV article

1. Create `submission/FINAL_DEV_ARTICLE.md` from `docs/DEV_ARTICLE_DRAFT.md`, replacing only placeholders for which real evidence exists. Use the official Hacktoberfest Week 2 submission template, not an unrelated article format. Avoid AI-sounding hype; be human, specific and technically honest.
2. Include screenshots with public URLs **only after uploading them to DEV/GitHub**; local relative paths won't render on DEV. Include a working video URL once hosted. State exact model actually run, how files were discovered, what hashes can/cannot guarantee, test result and limitations. Cite the paper and avoid claiming new research, paying customers, complete dependency discovery, or genuine deployment security.
3. Existing README, LICENSE and CONTRIBUTING must remain. Ensure no credentials, `.env`, sensitive information, binary caches, temp approvals or unrelated local files are committed. Use `.gitignore` and check `git status`.
4. Prepare a new public GitHub repository named `shadowinputs`. If GitHub CLI/auth exists and the user has approved publication, publish; otherwise print exact next commands/UI steps without inventing a URL. Verify public repo URL and demo video URL in a private/incognito view if possible.
5. Publish the DEV post through the official challenge submission route only with my authorization and access to the logged-in account. If web actions aren't available, hand me a ready-to-paste article and exact click instructions. Verify the published URL and contest association. Never say published if not actually done.
6. Claim Best Use of Gemma only if live local Gemma inference is successfully demonstrated. Keep disclosures if it fails. Do not fabricate production users or financial results.

## Time management and output contract

Deadline: 2026-10-19 12:29 PM IST. Prioritize actual working verification > real AI run > visual evidence > public repo/video > article/post. Do not spend time on UI redesign, integrations, SEO, branding or adding sponsors. Don't spend 30 minutes on a broken tool before offering a smaller verified fallback.

Show a concise status after each stage, with PASS/FAIL/NOT RUN and the exact evidence path. Do not ask questions unless credentials/permission/hardware are truly needed. At the end, provide:
- exact test output and Gemma status;
- all screenshot/video file paths, identifying whether genuinely captured or pre-existing;
- repo URL and video URL if confirmed, otherwise 'not published';
- ready final DEV article path;
- any remaining manual actions with the shortest steps;
- no more than 5 bullet points describing unresolved risks.

Begin by reading the project files and running tests. Do not start by rewriting the project.
