# Week 2: fast publishing checklist

**Verified official cutoff:** October 18, 2026, 11:59 PM PDT = **October 19, 2026, 12:29 PM IST**. If your signed-in page currently accepts submission, use that; public pages can show contradictory statuses. Don't change creation or publication dates to bypass eligibility.

## 0. Reality check

- [x] Brand-new standalone project files prepared as a ZIP.
- [x] Synthetic deterministic CLI demo executed, all four expected outcomes observed.
- [x] 21 Python tests passed in the build environment.
- [x] Local Gemma HTTP integration unit-tested with a simulated response.
- [ ] **LIVE GEMMA INFERENCE NOT YET RUN HERE.** Run on your Windows laptop and keep accurate evidence.
- [ ] GitHub repository uploaded (requires your authentication).
- [ ] Real demo video recorded and linked (requires your machine or a hosted video file).
- [ ] DEV post submitted (requires your signed-in account).

## 1. Make a NEW public GitHub repo

Repo suggestion: `shadowinputs`. Unzip, `cd shadowinputs`, then:

```powershell
git init
git add .
git commit -m "Build ShadowInputs local approval drift prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shadowinputs.git
git push -u origin main
```

Create the empty public repository first. Avoid GitHub's auto-initialized README when creating it, or reconcile the extra commit. Replace `YOUR_USERNAME`.

## 2. Run the actual model for eligible AI evidence

```powershell
ollama pull gemma3:4b
# Ensure Ollama desktop/server is running
py -m shadowinputs inspect --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --model gemma3:4b --output ai-review.json
```

Look for `MODEL_RETURNED_UNTRUSTED_CANDIDATES`. If `NOT_EVALUATED`, resolve the local Ollama failure first. `ai-review.json` is ignored by git to keep source-related inspection out of commits. Verify proposed paths yourself. Do not claim model quality beyond the one observed run.

## 3. Record a real demo

Minimum video outline, 60–90 seconds:
1. 0–10s: Show `deploy.py` reads `policy.json` and state why a script-only review can miss the change.
2. 10–30s: Execute the **real** `inspect` command with Gemma and show the model status; do not use a mock response.
3. 30–45s: Show `approve` and `verify` PASS with a manifest stored outside the sample directory.
4. 45–65s: Change `require_human_review` true → false, show `verify` BLOCK and nonzero status.
5. 65–80s: Show `python -m pytest -q`, limitations and the GitHub link.

You can also run `py -m demo.run_demo` to show all deterministic scenarios safely. Capture with OBS / Windows Snipping Tool recorder / Xbox Game Bar, then upload video to YouTube unlisted or another host with a stable public URL. Do not pass a video as live Gemma proof if it contains only the deterministic demo.

## 4. DEV article, formatting and submission

- Copy `docs/DEV_ARTICLE_DRAFT.md` into the official challenge's **Submission Template** (not an arbitrary post template if a button is available).
- Replace `[YOUR_GITHUB_REPO_URL]`, `[YOUR_VIDEO_DEMO_URL]` and the local-model evidence placeholder with real values.
- **Delete drafting instructions and placeholders.** Don't copy the `published: false` frontmatter verbatim if composing in the DEV UI.
- Keep `#devchallenge` and `#hf26challenge` and proper Week 2 contest association.
- Add **Best Use of Gemma** only after real Gemma inference evidence exists.
- Remove optional sections with no verified content (Agent Session, First User).
- Preview, verify links in an incognito browser, and publish before the deadline.
- Keep the description of the limits: no real production deployment, no customer, no complete input analysis.
- Confirm post appears in the appropriate challenge and capture the public link.

## 5. If model does not run before cutoff

Don't fabricate results. You can publish with a truthful disclosure about implemented integration and incomplete live validation, but prize eligibility and open-AI-at-core judging will be weaker. The contest requires more than a working hash tool; actual open-weight model use materially strengthens eligibility.
