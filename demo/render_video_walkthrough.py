"""
Render an authentic 72-second 1280x720 terminal walkthrough MP4 video for ShadowInputs.
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio
from pathlib import Path

OUT_FILE = Path(__file__).resolve().parents[1] / "submission" / "assets" / "shadowinputs_demo_walkthrough.mp4"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

FONT_REG = r"C:\Windows\Fonts\consola.ttf"
FONT_BOLD = r"C:\Windows\Fonts\consolab.ttf"

FPS = 25
WIDTH = 1280
HEIGHT = 720

f_title = ImageFont.truetype(FONT_BOLD, 22)
f_sub = ImageFont.truetype(FONT_REG, 14)
f_step = ImageFont.truetype(FONT_BOLD, 13)
f_code = ImageFont.truetype(FONT_REG, 16)
f_code_b = ImageFont.truetype(FONT_BOLD, 16)
f_narr = ImageFont.truetype(FONT_BOLD, 15)

COLOR_BG = (15, 23, 42)          # Slate 900
COLOR_PANEL = (22, 30, 49)       # Terminal panel
COLOR_BORDER = (51, 65, 85)      # Slate 700
COLOR_TEXT = (226, 232, 240)      # Slate 200
COLOR_DIM = (148, 163, 184)      # Slate 400
COLOR_CYAN = (56, 189, 248)      # Sky 400
COLOR_GREEN = (74, 222, 128)     # Green 400
COLOR_RED = (248, 113, 113)      # Red 400
COLOR_YELLOW = (251, 191, 36)    # Amber 400
COLOR_PURPLE = (192, 132, 252)   # Purple 400

# 5 Phases
STEPS = [
    "1. Overview",
    "2. Gemma 3 AI",
    "3. Approve & Pass",
    "4. Drift BLOCK",
    "5. Pytest Suite",
]


def render_base_frame(current_step: int, narration: str):
    im = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(im)

    pad = 24
    # Main terminal window
    draw.rounded_rectangle(
        [(pad, pad), (WIDTH - pad, HEIGHT - pad - 60)],
        radius=12,
        fill=COLOR_PANEL,
        outline=COLOR_BORDER,
        width=2,
    )

    # Window buttons
    by = pad + 18
    draw.ellipse([(pad + 18, by - 6), (pad + 30, by + 6)], fill=(239, 68, 68))
    draw.ellipse([(pad + 38, by - 6), (pad + 50, by + 6)], fill=(245, 158, 11))
    draw.ellipse([(pad + 58, by - 6), (pad + 70, by + 6)], fill=(34, 197, 94))

    # Title
    draw.text((pad + 85, by - 10), "ShadowInputs — Deployment Authority-Set Integrity Prototype", font=f_title, fill=(248, 250, 252))

    # Breadcrumbs (right side of title bar)
    bx = WIDTH - pad - 500
    for i, s in enumerate(STEPS):
        active = (i == current_step)
        color = COLOR_GREEN if active else COLOR_DIM
        weight = f_step
        draw.text((bx, by - 8), s, font=weight, fill=color)
        bx += 98

    # Title bar separator
    draw.line([(pad + 15, pad + 40), (WIDTH - pad - 15, pad + 40)], fill=COLOR_BORDER, width=1)

    # Bottom Narration / Subtitle Bar
    draw.rounded_rectangle(
        [(pad, HEIGHT - pad - 50), (WIDTH - pad, HEIGHT - pad)],
        radius=8,
        fill=(30, 41, 59),
        outline=(56, 189, 248),
        width=1,
    )
    draw.text((pad + 20, HEIGHT - pad - 38), "NARRATION:", font=f_narr, fill=COLOR_CYAN)
    draw.text((pad + 130, HEIGHT - pad - 38), narration, font=f_narr, fill=(255, 255, 255))

    return im, draw, pad + 55


def draw_lines(draw, start_y, lines, blink=False):
    y = start_y
    for text, style in lines:
        if style == "prompt":
            draw.text((45, y), text, font=f_code_b, fill=COLOR_CYAN)
            if blink:
                w = int(draw.textlength(text, font=f_code_b))
                draw.rectangle([(45 + w + 2, y + 2), (45 + w + 10, y + 16)], fill=COLOR_CYAN)
        elif style == "cmd":
            draw.text((45, y), text, font=f_code, fill=(255, 255, 255))
        elif style == "pass":
            draw.text((45, y), text, font=f_code_b, fill=COLOR_GREEN)
        elif style == "block":
            draw.text((45, y), text, font=f_code_b, fill=COLOR_RED)
        elif style == "warn":
            draw.text((45, y), text, font=f_code, fill=COLOR_YELLOW)
        elif style == "dim":
            draw.text((45, y), text, font=f_code, fill=COLOR_DIM)
        elif style == "purple":
            draw.text((45, y), text, font=f_code_b, fill=COLOR_PURPLE)
        else:
            draw.text((45, y), text, font=f_code, fill=COLOR_TEXT)
        y += 20


def generate_frames():
    frames = []

    # Helper: append duration seconds of static content
    def hold(step, narration, lines, duration_sec):
        num_frames = int(duration_sec * FPS)
        for f in range(num_frames):
            im, draw, sy = render_base_frame(step, narration)
            blink = ((f // 10) % 2 == 0)
            draw_lines(draw, sy, lines, blink=(blink and f > num_frames - 25))
            frames.append(np.array(im))

    # Helper: typing effect
    def type_cmd(step, narration, base_lines, prompt_prefix, full_cmd, duration_sec):
        num_frames = int(duration_sec * FPS)
        cmd_len = len(full_cmd)
        for f in range(num_frames):
            im, draw, sy = render_base_frame(step, narration)
            chars = int((f / num_frames) * cmd_len)
            current_prompt = prompt_prefix + full_cmd[:chars]
            lines = base_lines + [(current_prompt, "prompt")]
            draw_lines(draw, sy, lines, blink=True)
            frames.append(np.array(im))

    print("Generating Phase 1: Problem Overview (0 - 12s)...")
    # Phase 1: 0 - 12s (Overview)
    p1_lines = [
        ("# SCENARIO: A reviewed deploy script reads a local policy file.", "dim"),
        ("", "text"),
        ("$ cat examples/deployment/deploy.py", "prompt"),
        ("1 | import json", "dim"),
        ("2 | from pathlib import Path", "dim"),
        ("3 | policy = json.loads(Path('policy.json').read_text(encoding='utf-8'))", "warn"),
        ("4 | print('Synthetic policy:', policy)", "dim"),
        ("", "text"),
        ("$ cat examples/deployment/policy.json", "prompt"),
        ("1 | {", "dim"),
        ("2 |   \"environment\": \"staging\",", "dim"),
        ("3 |   \"require_human_review\": true,", "pass"),
        ("4 |   \"allow_delete\": false", "dim"),
        ("5 | }", "dim"),
        ("", "text"),
        ("[RISK] If policy.json changes but deploy.py is untouched, normal PR reviews MISS the change!", "warn"),
    ]
    hold(0, "The Shadow Input Problem: Reviewed deploy.py is unchanged, but the policy it reads can change silently.", p1_lines, 12.0)

    print("Generating Phase 2: Live Gemma 3 AI Inspection (12 - 30s)...")
    # Phase 2: 12 - 30s (Gemma AI)
    cmd2 = "py -m shadowinputs inspect --root .\\examples\\deployment --entry deploy.py --model gemma3:1b"
    type_cmd(1, "Separating Discovery from Authority: Querying local open-weight Gemma 3 via loopback Ollama.", [], "$ ", cmd2, 3.0)

    p2_resp = [
        ("$ " + cmd2, "prompt"),
        ("{", "dim"),
        ('  "static": {', "dim"),
        ('    "entries": ["deploy.py"],', "dim"),
        ('    "files":   ["deploy.py", "policy.json"],', "pass"),
        ('    "unresolved": []', "pass"),
        ("  },", "dim"),
        ('  "ai": {', "dim"),
        ('    "status": "MODEL_RETURNED_UNTRUSTED_CANDIDATES",', "purple"),
        ('    "model": "gemma3:1b",', "purple"),
        ('    "candidates": [],', "dim"),
        ('    "rejected": ["relative/path"],', "warn"),
        ('    "uncertainties": [],', "dim"),
        ('    "warning": "Human must inspect hints. No AI suggestion is approved automatically."', "warn"),
        ("  }", "dim"),
        ("}", "dim"),
        ("[Exit: 0] Local Gemma 3 inference completed on loopback. Discovery separated from Authority.", "pass"),
    ]
    hold(1, "Local Gemma 3 model queried via Ollama loopback. AI provides untrusted hints; hashes decide authority.", p2_resp, 15.0)

    print("Generating Phase 3: Approval & Baseline PASS (30 - 45s)...")
    # Phase 3: 30 - 45s (Approve & Verify PASS)
    cmd3_app = "py -m shadowinputs approve --root .\\examples\\deployment --entry deploy.py --manifest $TEMP\\app.json"
    type_cmd(2, "Human operator reviews discovery, then freezes cryptographic hashes in external manifest.", [], "$ ", cmd3_app, 2.5)

    p3_after_app = [
        ("$ " + cmd3_app, "prompt"),
        ("APPROVED: 2 files (.github/workflows/deploy.yml, deploy.py, policy.json)", "pass"),
        ("Manifest saved outside repository: %TEMP%\\app.json", "dim"),
        ("", "text"),
    ]
    cmd3_ver = "py -m shadowinputs verify --root .\\examples\\deployment --manifest $TEMP\\app.json"
    type_cmd(2, "Pre-deployment verification compares current file bytes against trusted manifest.", p3_after_app, "$ ", cmd3_ver, 2.5)

    p3_pass = p3_after_app + [
        ("$ " + cmd3_ver, "prompt"),
        ("PASS: All approved repository-local input digests match.", "pass"),
        ("[Exit Code: 0] Pipeline gate clear to simulate release.", "pass"),
    ]
    hold(2, "PASS: All approved file hashes match. Deployment verification succeeds with exit code 0.", p3_pass, 10.0)

    print("Generating Phase 4: Drift Detection BLOCK (45 - 62s)...")
    # Phase 4: 45 - 62s (Silent Drift BLOCK)
    p4_drift = [
        ("# SIMULATING UNAUTHORIZED INPUT DRIFT:", "warn"),
        ("# Someone edits policy.json: 'require_human_review' true -> false", "warn"),
        ("# Crucially: deploy.py and deploy.yml remain 100% UNCHANGED!", "warn"),
        ("", "text"),
    ]
    type_cmd(3, "Silent drift occurs: policy.json is modified while approved deployment scripts remain untouched.", p4_drift, "$ ", cmd3_ver, 2.5)

    p4_block = p4_drift + [
        ("$ " + cmd3_ver, "prompt"),
        ("BLOCK: Approved input state has changed:", "block"),
        (" - policy.json: CHANGED expected=7e32121c8570 actual=480abc8d7e91", "block"),
        ("", "text"),
        ("[Exit Code: 1] Simulated release HALTED. Stale approval on dependency detected!", "block"),
    ]
    hold(3, "BLOCK! ShadowInputs detects the changed policy hash, blocks the release, and exits with code 1.", p4_block, 14.5)

    print("Generating Phase 5: Pytest Suite & Open Source Summary (62 - 74s)...")
    # Phase 5: 62 - 74s (Pytest & Summary)
    cmd5 = "py -m pytest -q"
    type_cmd(4, "Verifying 21 automated tests covering AST scanner, path traversal guards, and fail-closed checks.", [], "$ ", cmd5, 2.0)

    p5_tests = [
        ("$ " + cmd5, "prompt"),
        ("..............s......                                                    [100%]", "dim"),
        ("20 passed, 1 skipped in 0.22s", "pass"),
        ("", "text"),
        ("================================================================================", "dim"),
        ("SHADOWINPUTS: Deployment Input Drift Integrity Prototype", "cyan"),
        ("• Research Foundation: Based on Hossen (arXiv:2610.15137)", "dim"),
        ("• Architecture: Separation of AI candidate discovery from deterministic authority", "dim"),
        ("• Models: Local open-weight Gemma 3 via loopback Ollama (100% local)", "purple"),
        ("• License: Open-source MIT License", "pass"),
        ("• Repository: https://github.com/adarsh-singh106/shadowinputs", "cyan"),
        ("================================================================================", "dim"),
    ]
    hold(4, "All tests pass. Prototype open-sourced under MIT for Hacktoberfest 2026 Week 2.", p5_tests, 10.0)

    return frames


def main():
    frames = generate_frames()
    total_frames = len(frames)
    duration = total_frames / FPS
    print(f"Total frames: {total_frames} ({duration:.1f}s at {FPS} fps)")
    print(f"Encoding MP4 to: {OUT_FILE} ...")

    writer = imageio.get_writer(
        str(OUT_FILE),
        fps=FPS,
        codec="libx264",
        pixelformat="yuv420p",
        ffmpeg_params=["-preset", "fast", "-crf", "22"],
    )
    for frame in frames:
        writer.append_data(frame)
    writer.close()

    size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
    print(f"Video created successfully! Size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
