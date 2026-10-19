# Manual Screenshot Guide (Optional Native OS Captures)

Rendered high-resolution terminal cards for all 3 key scenarios have already been generated in:
- `submission/assets/01_pytest_verification.png`
- `submission/assets/02_gemma_inspection.png`
- `submission/assets/03_pass_and_block_cli.png`
- `submission/assets/04_deterministic_scenarios.png`

If you would like to capture native OS terminal screenshots using the Windows Snipping Tool (`Win + Shift + S`), follow these commands:

---

### Screenshot 1: Automated Test Suite (pytest)
In PowerShell:
```powershell
py -m pytest -v
```
Press `Win + Shift + S`, select window or rectangle, and save as `submission/assets/native_pytest.png`.

---

### Screenshot 2: Real Gemma 3 Inspection (Ollama)
In PowerShell:
```powershell
py -m shadowinputs inspect --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --model gemma3:1b --output ai-review.json
```
Press `Win + Shift + S`, select window or rectangle, and save as `submission/assets/native_gemma_inspect.png`.

---

### Screenshot 3: PASS and BLOCK Drift Demonstration
In PowerShell:
```powershell
# Approve
py -m shadowinputs approve --root .\examples\deployment --entry .github/workflows/deploy.yml --entry deploy.py --manifest "$env:TEMP\shadowinputs-approval.json"

# Verify baseline (PASS)
py -m shadowinputs verify --root .\examples\deployment --manifest "$env:TEMP\shadowinputs-approval.json"

# Temporarily edit policy.json (set "require_human_review": false)
(Get-Content examples\deployment\policy.json) -replace 'true', 'false' | Set-Content examples\deployment\policy.json

# Verify drift (BLOCK)
py -m shadowinputs verify --root .\examples\deployment --manifest "$env:TEMP\shadowinputs-approval.json"

# Restore policy.json
(Get-Content examples\deployment\policy.json) -replace 'false', 'true' | Set-Content examples\deployment\policy.json
```
Press `Win + Shift + S`, select window or rectangle, and save as `submission/assets/native_cli_block.png`.
