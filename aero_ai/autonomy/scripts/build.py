#!/usr/bin/env python3
"""
aero_ai/autonomy/scripts/build.py

Automates the complete edge autonomy pipeline:
1. Normalize raw telemetry / blackbox logs and generate scaling stats
2. Train FlightSafetyNet MLP / 1D-CNN (saves checkpoints/best.pth)
3. Evaluate model classification accuracy, F1, and confusion matrix
4. Quantize PyTorch model to int8 TFLite and generate C header (.h)
5. (Optional) Run interactive package/deployment step

Usage:
    python scripts/build.py                 # Full pipeline (train -> eval -> export)
    python scripts/build.py --sync-edge     # Full pipeline + launch interactive packaging
    python scripts/build.py --skip-train    # Skip train (run eval -> export)
    python scripts/build.py --only-export   # Direct quantization & C-header generation
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


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


def run_package_step(dest: str | None = None):
    print_step("Deploying to Edge Subsystems")
    package_script = SCRIPT_DIR / "package.py"
    cmd = [sys.executable, str(package_script)]
    if dest:
        cmd.extend(["--dest", dest])

    # Direct execution so interactive inputs/prompts work seamlessly
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("\n❌ [ERROR] Packaging failed or was cancelled.")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="ResQVision Flight Autonomy Build Automation")
    parser.add_argument("--sync-edge", action="store_true", help="Launch interactive packager after build")
    parser.add_argument("--dest", help="Direct destination directory (skips packaging prompt)")
    parser.add_argument("--skip-prep", action="store_true", help="Skip data preprocessing / normalization")
    parser.add_argument("--skip-train", action="store_true", help="Skip model training step")
    parser.add_argument("--skip-eval", action="store_true", help="Skip evaluation benchmark")
    parser.add_argument("--only-export", action="store_true", help="Run only the TFLite/C-header export step")
    parser.add_argument("--config", default="configs/flight_safety.yaml", help="Path to config file")
    args = parser.parse_args()

    python_bin = sys.executable

    print("\n" + "#" * 65)
    print("     RESQVISION FLIGHT AUTONOMY PIPELINE BUILD AUTOMATION     ")
    print("#" * 65)

    # Fast path: Only export
    if args.only_export:
        print_step("Direct Quantization & C Header Export")
        run_command(
            [
                python_bin, "-m", "aero_autonomy_ai.cli", "export",
                "--config", args.config,
                "--checkpoint", "checkpoints/best.pth",
            ],
            "TFLite / C-Header Export",
        )
        if args.sync_edge or args.dest:
            run_package_step(args.dest)
        print("\n🎉 Export step finished.")
        return

    # Step 1: Preprocess raw flight telemetry logs
    if not args.skip_prep:
        raw_data_dir = PROJECT_ROOT / "data" / "raw"
        if any(raw_data_dir.glob("*.csv")):
            print_step("1/4: Preprocessing & Computing Normalization Stats")
            run_command(
                [python_bin, "-m", "aero_autonomy_ai.cli", "prepare", "--config", args.config],
                "Data Preprocessing",
            )
        else:
            print("[!] No CSV logs in data/raw/; skipping preprocessing step.")
    else:
        print("[!] Skipping data preparation step.")

    # Step 2: Train
    if not args.skip_train:
        print_step("2/4: Training Flight Safety Decision Model")
        run_command(
            [python_bin, "-m", "aero_autonomy_ai.cli", "train", "--config", args.config],
            "Model Training",
        )
    else:
        print("[!] Skipping Model Training step.")

    # Step 3: Evaluate
    if not args.skip_eval:
        print_step("3/4: Flight Safety Decision Evaluation (F1 / Confusion Matrix)")
        run_command(
            [
                python_bin, "-m", "aero_autonomy_ai.cli", "evaluate",
                "--config", args.config,
                "--checkpoint", "checkpoints/best.pth",
                "--output", "artifacts/evaluation.json",
            ],
            "Evaluation Benchmark",
        )
    else:
        print("[!] Skipping Evaluation step.")

    # Step 4: Quantize & Export
    print_step("4/4: int8 Post-Training Quantization & C Header Generation")
    run_command(
        [
            python_bin, "-m", "aero_autonomy_ai.cli", "export",
            "--config", args.config,
            "--checkpoint", "checkpoints/best.pth",
        ],
        "TFLite & C Header Export",
    )

    # Optional Step 5: Packaging / Sync
    if args.sync_edge or args.dest:
        run_package_step(args.dest)

    print("\n" + "=" * 65)
    print("🎉 [COMPLETE] ResQVision Autonomy pipeline completed successfully!")
    print(f"📦 Output artifacts saved to: {ARTIFACTS_DIR.resolve()}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()