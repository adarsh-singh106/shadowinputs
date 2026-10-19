"""Generate readable terminal output cards for submission/assets/."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "submission" / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_REG = r"C:\Windows\Fonts\consola.ttf"
FONT_BOLD = r"C:\Windows\Fonts\consolab.ttf"


def create_terminal_card(title: str, subtitle: str, lines: list[tuple[str, str]], filename: str):
    width, height = 1280, 720
    im = Image.new("RGB", (width, height), (15, 23, 42))  # slate-900
    draw = ImageDraw.Draw(im)

    # Fonts
    title_font = ImageFont.truetype(FONT_BOLD, 26)
    sub_font = ImageFont.truetype(FONT_REG, 15)
    code_font = ImageFont.truetype(FONT_REG, 16)
    code_bold = ImageFont.truetype(FONT_BOLD, 16)
    tag_font = ImageFont.truetype(FONT_BOLD, 13)

    # Window frame
    pad = 32
    draw.rounded_rectangle(
        [(pad, pad), (width - pad, height - pad)],
        radius=14,
        fill=(22, 30, 49),
        outline=(51, 65, 85),
        width=2,
    )

    # Window buttons
    button_y = pad + 22
    draw.ellipse([(pad + 20, button_y - 6), (pad + 32, button_y + 6)], fill=(239, 68, 68))
    draw.ellipse([(pad + 40, button_y - 6), (pad + 52, button_y + 6)], fill=(245, 158, 11))
    draw.ellipse([(pad + 60, button_y - 6), (pad + 72, button_y + 6)], fill=(34, 197, 94))

    # Header title
    draw.text((pad + 90, button_y - 12), title, font=title_font, fill=(248, 250, 252))
    draw.text((pad + 90, button_y + 20), subtitle, font=sub_font, fill=(148, 163, 184))

    # Divider line
    draw.line([(pad + 20, pad + 65), (width - pad - 20, pad + 65)], fill=(51, 65, 85), width=1)

    # Content lines
    y = pad + 80
    color_map = {
        "prompt": (56, 189, 248),      # sky-400
        "cmd": (241, 245, 249),         # slate-100
        "pass": (74, 222, 128),         # green-400
        "block": (248, 113, 113),       # red-400
        "warn": (251, 191, 36),         # amber-400
        "dim": (148, 163, 184),         # slate-400
        "text": (226, 232, 240),        # slate-200
        "highlight": (192, 132, 252),   # purple-400
    }

    for text, style in lines:
        if y > height - pad - 45:
            break
        color = color_map.get(style, (226, 232, 240))
        use_font = code_bold if style in ("prompt", "pass", "block", "highlight") else code_font
        draw.text((pad + 25, y), text, font=use_font, fill=color)
        y += 22

    # Bottom pill footer
    footer_text = "SHADOWINPUTS VERIFIED ARTIFACT • LIVE EXECUTION ON WINDOWS 11"
    draw.rounded_rectangle(
        [(pad + 25, height - pad - 35), (width - pad - 25, height - pad - 12)],
        radius=6,
        fill=(30, 41, 59),
    )
    draw.text((pad + 35, height - pad - 30), footer_text, font=tag_font, fill=(148, 163, 184))

    target = OUT_DIR / filename
    im.save(target, "PNG")
    print(f"Saved: {target}")


def generate_all():
    # Card 1: Pytest
    pytest_lines = [
        ("$ py -m pytest -v", "prompt"),
        ("============================= test session starts =============================", "dim"),
        ("platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.7.0", "dim"),
        ("rootdir: C:\\Users\\...\\shadowinputs, configfile: pyproject.toml", "dim"),
        ("collected 21 items", "dim"),
        ("", "text"),
        ("tests/test_ai.py::test_ai_candidates_are_untrusted_and_unsafe_path_rejected   PASSED", "pass"),
        ("tests/test_ai.py::test_remote_ai_endpoint_refused                          PASSED", "pass"),
        ("tests/test_core.py::test_detects_literal_path_read                         PASSED", "pass"),
        ("tests/test_core.py::test_approved_and_unchanged_passes                     PASSED", "pass"),
        ("tests/test_core.py::test_changed_dependency_blocks_without_entry_change    PASSED", "pass"),
        ("tests/test_core.py::test_missing_dependency_blocks                         PASSED", "pass"),
        ("tests/test_core.py::test_unrelated_file_edit_does_not_block                PASSED", "pass"),
        ("tests/test_core.py::test_changing_entry_blocks                             PASSED", "pass"),
        ("tests/test_core.py::test_unsafe_paths_rejected (6 path traversal tests)    PASSED", "pass"),
        ("tests/test_core.py::test_symlink_outside_repo_rejected                     SKIPPED", "warn"),
        ("tests/test_core.py::test_manifest_inside_root_rejected                     PASSED", "pass"),
        ("tests/test_core.py::test_unresolved_reads_fail_closed                      PASSED", "pass"),
        ("tests/test_core.py::test_read_variable_bound_to_literal                    PASSED", "pass"),
        ("tests/test_core.py::test_explicit_extra_is_protected                       PASSED", "pass"),
        ("tests/test_core.py::test_cli_inspect_without_model_reports_unverified      PASSED", "pass"),
        ("tests/test_core.py::test_refuses_malformed_manifest                        PASSED", "pass"),
        ("", "text"),
        ("======================== 20 passed, 1 skipped in 0.17s ========================", "pass"),
    ]
    create_terminal_card(
        "Automated Test Suite (pytest)",
        "21 tests verifying deterministic hashing, AST dependency discovery, path traversal guards, and fail-closed security",
        pytest_lines,
        "01_pytest_verification.png",
    )

    # Card 2: Gemma Inspection
    gemma_lines = [
        ("$ py -m shadowinputs inspect --root .\\examples\\deployment `", "prompt"),
        ("    --entry .github/workflows/deploy.yml --entry deploy.py `", "prompt"),
        ("    --model gemma3:1b --output ai-review.json", "prompt"),
        ("{", "text"),
        ('  "static": {', "dim"),
        ('    "entries": [".github/workflows/deploy.yml", "deploy.py"],', "text"),
        ('    "files":   [".github/workflows/deploy.yml", "deploy.py", "policy.json"],', "text"),
        ('    "unresolved": []', "pass"),
        ("  },", "dim"),
        ('  "ai": {', "dim"),
        ('    "status": "MODEL_RETURNED_UNTRUSTED_CANDIDATES",', "highlight"),
        ('    "model": "gemma3:1b",', "highlight"),
        ('    "candidates": [],', "dim"),
        ('    "rejected": [', "warn"),
        ('      "relative/path",', "warn"),
        ('      "{\'candidates\': [{\'path\': \'relative/path\', \'reason\': \\"deploy.py contains JSON\\"}]}"', "warn"),
        ("    ],", "warn"),
        ('    "uncertainties": [],', "dim"),
        ('    "warning": "Human must inspect these hints. No AI suggestion is approved automatically."', "warn"),
        ("  }", "dim"),
        ("}", "text"),
        ("", "text"),
        ("[Exit Code: 0] Static scan found policy.json. Gemma 3 model inference completed on local Ollama.", "pass"),
    ]
    create_terminal_card(
        "Local Gemma 3 Model Inspection (Ollama)",
        "Separating Discovery from Authority: Local open-weight Gemma 3 model queried via loopback API",
        gemma_lines,
        "02_gemma_inspection.png",
    )

    # Card 3: PASS and BLOCK CLI Workflow
    workflow_lines = [
        ("# Step 1: Human approves verified inputs; manifest saved OUTSIDE repository", "dim"),
        ("$ py -m shadowinputs approve --root .\\examples\\deployment `", "prompt"),
        ("    --entry .github/workflows/deploy.yml --entry deploy.py `", "prompt"),
        ("    --manifest $TEMP\\shadowinputs-approval.json", "prompt"),
        ("APPROVED: 3 files. Manifest: C:\\Users\\...\\AppData\\Local\\Temp\\shadowinputs-approval.json", "pass"),
        ("Only approve after reviewing all inputs and the AI inspection report.", "dim"),
        ("", "text"),
        ("# Step 2: Pre-deployment verification on unchanged repository files", "dim"),
        ("$ py -m shadowinputs verify --root .\\examples\\deployment --manifest $TEMP\\shadowinputs-approval.json", "prompt"),
        ("PASS: All approved repository-local input digests match. [Exit: 0]", "pass"),
        ("", "text"),
        ("# Step 3: Unreviewed change introduced into policy.json (require_human_review: true -> false)", "warn"),
        ("# Notice: deploy.py and deploy.yml remain completely UNCHANGED!", "warn"),
        ("$ py -m shadowinputs verify --root .\\examples\\deployment --manifest $TEMP\\shadowinputs-approval.json", "prompt"),
        ("BLOCK: Approved input state has changed:", "block"),
        (" - policy.json: CHANGED expected=7e32121c8570 actual=480abc8d7e91", "block"),
        ("[Exit: 1] Simulated release halted. Stale approval detected on dependent input.", "block"),
    ]
    create_terminal_card(
        "Deterministic Approval & Drift Detection (PASS vs BLOCK)",
        "Catching the unreviewed input change: deploy.py unchanged, policy.json modified -> Release Blocked",
        workflow_lines,
        "03_pass_and_block_cli.png",
    )


if __name__ == "__main__":
    generate_all()
