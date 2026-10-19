# Screen Recording Storyboard & Operator Checklist

This checklist guides the operator through capturing an authentic **60–90 second screen recording** of ShadowInputs for the Hacktoberfest 2026 Week 2 submission.

---

## 1. Quick Capture Setup (Windows Built-in Tools)

1. **Option A (Snipping Tool Screen Recorder - Recommended):**
   - Press `Win + Shift + R`.
   - Select your terminal area (or full screen 1080p).
   - Ensure microphone audio is toggled ON (or add captions/subtitles).
   - Click **Start** (gives a 3-second countdown).

2. **Option B (Xbox Game Bar):**
   - Press `Win + Alt + R` to start/stop recording immediately.

3. **Option C (OBS Studio):**
   - Window Capture or Display Capture at 1920x1080 30/60fps.

---

## 2. Interactive One-Command Runner

Open a PowerShell terminal in the repository root (`C:\Users\adars\Desktop\One ML\Hacktoberfest\Week 2\shadowinputs`) and run:

```powershell
.\demo\run_live_walkthrough.ps1
```

The script pauses at each stage, guiding you through the exact 5 steps below. Simply press `Enter` to step forward.

---

## 3. Storyboard & Timing Breakdown (Target: 60–90 seconds)

| Timestamp | Phase | What's on Screen | Talk Track / Voiceover |
|---|---|---|---|
| **00:00 – 00:12** | **The Problem (Shadow Inputs)** | Displaying `deploy.py` and `policy.json`. | *"In modern CI/CD, approving a deployment script like deploy.py isn't enough if the script silently reads other repository inputs like policy.json. When policy.json changes without touching deploy.py, standard PR and workflow reviews miss it."* |
| **00:12 – 00:32** | **Live AI Inspection (Gemma 3 / Ollama)** | Running `py -m shadowinputs inspect ... --model gemma3:1b`. JSON report with `MODEL_RETURNED_UNTRUSTED_CANDIDATES`. | *"ShadowInputs separates discovery from authority. We use a local open-weight Gemma 3 model via Ollama to inspect the repository and propose candidate dependencies without trusting the AI to grant approval."* |
| **00:32 – 00:48** | **Approval & Baseline Verification** | Running `shadowinputs approve` then `verify`. Clean `PASS`. | *"Once reviewed, we approve the inputs into a cryptographic manifest stored outside the mutable workspace. Running verify confirms the baseline state matches with exit code 0."* |
| **00:48 – 00:68** | **Drift Detection (PASS -> BLOCK)** | `policy.json` edited (`require_human_review: false`), `verify` run -> `BLOCK: policy.json CHANGED`. | *"Now, suppose an unreviewed change flips require_human_review to false. Notice deploy.py is completely unchanged. Pre-deployment verify immediately catches the hash mismatch, blocks the run, and exits with code 1."* |
| **00:68 – 00:85** | **Test Suite & Limitations** | Running `py -m pytest -q` (20 passed, 1 skipped). Brief overview of MIT repo. | *"20 automated tests verify our AST scanner, path traversal guards, and fail-closed integrity. The project is open-source under MIT on GitHub."* |

---

## 4. After Recording

1. Stop recording (`Win + Shift + R` or `Win + Alt + R`).
2. Save the video file as `submission/assets/shadowinputs_live_demo.mp4`.
3. Upload to YouTube (Unlisted or Public) or GitHub Releases / Google Drive.
4. Paste the public URL into `submission/FINAL_DEV_ARTICLE.md`.
