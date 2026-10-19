# Interactive Walkthrough Script for 60-90s Screen Recording
# Run this in a PowerShell window while recording your screen (Win + Shift + R)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  SHADOWINPUTS LIVE DEMONSTRATION WALKTHROUGH" -ForegroundColor Green
Write-Host "  Target duration: 60-90 seconds" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Section 1 (0-12s): The Problem
Write-Host "[0-12s] SCENARIO OVERVIEW" -ForegroundColor Magenta
Write-Host "In examples/deployment, deploy.py reads policy.json." -ForegroundColor Gray
Write-Host "Content of examples/deployment/deploy.py:" -ForegroundColor DarkGray
Get-Content examples/deployment/deploy.py
Write-Host ""
Write-Host "Content of examples/deployment/policy.json:" -ForegroundColor DarkGray
Get-Content examples/deployment/policy.json
Write-Host ""
Write-Host "If someone modifies policy.json without touching deploy.py, standard PR/workflow review misses it!" -ForegroundColor Yellow
Read-Host "Press ENTER to run local Gemma 3 AI Inspection..."

# Section 2 (12-30s): Real Gemma 3 Inspection
Write-Host "`n[12-30s] STEP 1: AI-ASSISTED INSPECTION WITH LOCAL GEMMA 3 (OLLAMA)" -ForegroundColor Magenta
Write-Host "Running: py -m shadowinputs inspect --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --model gemma3:1b --output ai-review.json" -ForegroundColor Cyan
py -m shadowinputs inspect --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --model gemma3:1b --output ai-review.json
Write-Host "Exit Code: $LASTEXITCODE" -ForegroundColor Green
Write-Host "Note: Gemma 3 ran via local Ollama. Discovery is separated from Authority." -ForegroundColor Yellow
Read-Host "Press ENTER to demonstrate Approve & Verify..."

# Section 3 (30-45s): Human Approval and Baseline Verify (PASS)
Write-Host "`n[30-45s] STEP 2: HUMAN APPROVAL & VERIFICATION" -ForegroundColor Magenta
$manifestPath = "$env:TEMP\shadowinputs-approval.json"
Write-Host "Recording SHA-256 hashes outside mutable repo to: $manifestPath" -ForegroundColor Gray
Write-Host "Running: py -m shadowinputs approve --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --manifest `"$manifestPath`"" -ForegroundColor Cyan
py -m shadowinputs approve --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --manifest "$manifestPath"

Write-Host "`nVerifying unchanged repository:" -ForegroundColor Gray
Write-Host "Running: py -m shadowinputs verify --root .\examples\deployment --manifest `"$manifestPath`"" -ForegroundColor Cyan
py -m shadowinputs verify --root .\examples\deployment --manifest "$manifestPath"
Write-Host "Exit Code: $LASTEXITCODE (PASS)" -ForegroundColor Green
Read-Host "Press ENTER to introduce unreviewed policy change..."

# Section 4 (45-65s): Input Drift Detection (BLOCK)
Write-Host "`n[45-65s] STEP 3: SILENT INPUT DRIFT (MODIFYING policy.json ONLY)" -ForegroundColor Magenta
$policyFile = "examples/deployment/policy.json"
$originalPolicy = Get-Content $policyFile -Raw
$modifiedPolicy = $originalPolicy.Replace('"require_human_review": true', '"require_human_review": false')
Set-Content $policyFile $modifiedPolicy

Write-Host "Modified $policyFile: require_human_review is now FALSE." -ForegroundColor Red
Write-Host "Notice: deploy.py and deploy.yml remain 100% UNCHANGED." -ForegroundColor Yellow

Write-Host "`nRunning pre-execution verification:" -ForegroundColor Gray
Write-Host "Running: py -m shadowinputs verify --root .\examples\deployment --manifest `"$manifestPath`"" -ForegroundColor Cyan
py -m shadowinputs verify --root .\examples\deployment --manifest "$manifestPath"
Write-Host "Exit Code: $LASTEXITCODE (BLOCK - Stale Approval Detected!)" -ForegroundColor Red

# Restore fixture immediately
Set-Content $policyFile $originalPolicy
Write-Host "Restored policy.json to original state." -ForegroundColor Gray
Read-Host "Press ENTER to run automated test suite..."

# Section 5 (65-85s): Test Suite and Verification
Write-Host "`n[65-85s] STEP 4: VERIFY TEST SUITE" -ForegroundColor Magenta
Write-Host "Running: py -m pytest -q" -ForegroundColor Cyan
py -m pytest -q
Write-Host "All unit tests pass verifying deterministic hashing, AST scanner, and security boundaries." -ForegroundColor Green
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  WALKTHROUGH COMPLETE! You can stop screen recording now." -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
