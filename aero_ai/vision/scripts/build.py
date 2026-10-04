#!/usr/bin/env python3
"""
aero_ai/vision/scripts/build.py

Automates the complete aerial object detection pipeline:
1. Validate COCO dataset integrity (train/val annotations and images)
2. Train Faster R-CNN detector (saves checkpoints/best.pt)
3. Evaluate model on validation set (mAP50, mAP75)
4. Export dynamic ONNX model and metadata sidecar
5. (Optional) Run interactive package/deployment step

Usage:
    python scripts/build.py                   # Full pipeline
    python scripts/build.py --sync-command    # Full pipeline + launch interactive packager
    python scripts/build.py --dest /path      # Full pipeline + deploy directly to destination
    python scripts/build.py --skip-train      # Validate -> Eval -> Export
    python scripts/build.py --only-export     # Direct export of checkpoints/best.pt
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"


def print_step(title: str):
    print("\n" + "=" * 65)
    print(f"🚀 [STEP] {title}")
    print("=" * 65)


def run_command(cmd: list[str], step_name: str):
    print(f"[*] Running: {' '.join(cmd)}")
    env = os.environ.copy()
    src_dir = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_dir}:{existing_pythonpath}" if existing_pythonpath else src_dir

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env)
    if result.returncode != 0:
        print(f"\n❌ [ERROR] {step_name} failed with exit code {result.returncode}!")
        sys.exit(result.returncode)
    print(f"✅ {step_name} finished successfully.")


def run_package_step(dest: str | None = None, local: bool = False):
    print_step("Deploying Vision Model Artifacts")
    package_script = SCRIPT_DIR / "package.py"
    cmd = [sys.executable, str(package_script)]
    if dest:
        cmd.extend(["--dest", dest])
    elif local:
        cmd.append("--local")

    # Inherit stdin/stdout directly for clean interactive prompts
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("\n❌ [ERROR] Packaging failed or was cancelled.")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="ResQVision Vision Pipeline Build Automation")
    parser.add_argument("--sync-command", action="store_true", help="Launch interactive packaging prompt after build")
    parser.add_argument("--dest", help="Direct destination directory (bypasses packaging prompt)")
    parser.add_argument("--local", action="store_true", help="Deploy directly to vision/dist/ (bypasses prompt)")
    parser.add_argument("--skip-validate", action="store_true", help="Skip dataset validation")
    parser.add_argument("--skip-train", action="store_true", help="Skip model training step")
    parser.add_argument("--skip-eval", action="store_true", help="Skip evaluation benchmark")
    parser.add_argument("--only-export", action="store_true", help="Run only the ONNX export step")
    parser.add_argument("--config", default="configs/detection.yaml", help="Path to config file")
    args = parser.parse_args()

    python_bin = sys.executable
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "#" * 65)
    print("      RESQVISION AERIAL DETECTION PIPELINE BUILD AUTOMATION      ")
    print("#" * 65)

    # Fast path: Only export
    if args.only_export:
        print_step("Direct ONNX Export")
        cmd = [
            python_bin, "-m", "aero_vision_ai.cli", "export",
            "--config", args.config,
            "--checkpoint", "checkpoints/best.pt",
            "--output", "artifacts/aero_detector.onnx",
        ]
        run_command(cmd, "ONNX Export")
        if args.sync_command or args.dest or args.local:
            run_package_step(dest=args.dest, local=args.local)
        print("\n🎉 Export step finished.")
        return

    # Step 1: Validate COCO dataset integrity
    if not args.skip_validate:
        print_step("1/4: Validating COCO Annotation Integrity")
        run_command(
            [python_bin, "-m", "aero_vision_ai.cli", "validate", "--config", args.config],
            "Dataset Validation",
        )
    else:
        print("[!] Skipping Dataset Validation step.")

    # Step 2: Train Faster R-CNN detector
    if not args.skip_train:
        print_step("2/4: Training Aerial Object Detector (Faster R-CNN)")
        run_command(
            [python_bin, "-m", "aero_vision_ai.cli", "train", "--config", args.config],
            "Model Training",
        )
    else:
        print("[!] Skipping Model Training step.")

    # Step 3: Evaluate detection metrics
    if not args.skip_eval:
        print_step("3/4: Detection Metrics Evaluation (mAP50 / mAP75)")
        run_command(
            [
                python_bin, "-m", "aero_vision_ai.cli", "evaluate",
                "--config", args.config,
                "--checkpoint", "checkpoints/best.pt",
                "--output", "artifacts/evaluation.json",
            ],
            "Evaluation Benchmark",
        )
    else:
        print("[!] Skipping Evaluation step.")

    # Step 4: Export to dynamic ONNX
    print_step("4/4: Dynamic ONNX Export & Metadata Sidecar")
    run_command(
        [
            python_bin, "-m", "aero_vision_ai.cli", "export",
            "--config", args.config,
            "--checkpoint", "checkpoints/best.pt",
            "--output", "artifacts/aero_detector.onnx",
        ],
        "ONNX Export",
    )

    # Optional Step 5: Packaging / Sync
    if args.sync_command or args.dest or args.local:
        run_package_step(dest=args.dest, local=args.local)

    print("\n" + "=" * 65)
    print("🎉 [COMPLETE] ResQVision Vision pipeline completed successfully!")
    print(f"📦 Output artifacts saved to: {ARTIFACTS_DIR.resolve()}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()