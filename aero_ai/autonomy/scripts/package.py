#!/usr/bin/env python3
"""
Interactive export script for ResQVision Autonomy edge models.
Deploys TFLite models, C-headers, and normalization stats interactively.
"""

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parents[1]  # ResQVision repo root
ARTIFACTS_DIR = ROOT / "artifacts"

SOURCE_TFLITE = ARTIFACTS_DIR / "safety_model_int8.tflite"
SOURCE_HEADER = ARTIFACTS_DIR / "safety_model.h"
SOURCE_STATS = ARTIFACTS_DIR / "normalization_stats.json"


def select_destination() -> tuple[Path, str]:
    targets = {
        "1": (
            "aero_flight firmware (C-Header only)",
            WORKSPACE_ROOT / "aero_flight" / "include" / "models",
            "header_only",
        ),
        "2": (
            "aero_app mobile / companion SBC (TFLite + Stats)",
            WORKSPACE_ROOT / "aero_app" / "assets" / "models",
            "tflite_bundle",
        ),
        "3": (
            "Local distribution folder (autonomy/dist - All Files)",
            ROOT / "dist",
            "all",
        ),
    }

    print("\n" + "=" * 60)
    print("📦 ResQVision Autonomy Edge Artifact Deployment")
    print("=" * 60)
    print("Select deployment target:\n")

    for key, (name, path, _) in targets.items():
        exists_mark = " [found]" if path.parent.exists() else ""
        print(f"  [{key}] {name}{exists_mark}")
        print(f"      -> {path}")

    print("  [4] Custom directory (deploy all generated files)")
    print("  [q] Cancel")

    while True:
        choice = input("\nEnter choice [1-4 / q] (default: 3): ").strip().lower() or "3"

        if choice in ("q", "quit", "exit"):
            print("\n[!] Deployment cancelled.")
            sys.exit(0)

        if choice in targets:
            dest_path = targets[choice][1]
            mode = targets[choice][2]
            break
        elif choice == "4":
            custom_str = input("Enter destination directory: ").strip()
            if not custom_str:
                print("Path cannot be empty. Try again.")
                continue
            dest_path = Path(custom_str).expanduser().resolve()
            mode = "all"
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, or q.")

    confirm = input(f"\nDeploy to:\n  {dest_path}\nProceed? [Y/n]: ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("[!] Aborted by user.")
        sys.exit(0)

    return dest_path, mode


def main():
    available_files = [f for f in (SOURCE_TFLITE, SOURCE_HEADER, SOURCE_STATS) if f.is_file()]
    if not available_files:
        print(f"\n❌ [ERROR] No exported artifacts found in: {ARTIFACTS_DIR}")
        print("Run 'python scripts/build.py' or 'aero-autonomy export' first.")
        sys.exit(1)

    dest_dir, mode = select_destination()
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("\n[*] Deploying files...")
    deployed = 0

    # Deploy C Header
    if mode in ("header_only", "all") and SOURCE_HEADER.is_file():
        dest = dest_dir / "safety_model.h"
        shutil.copy2(SOURCE_HEADER, dest)
        print(f"  [✓] C Header (.h)     -> {dest}")
        deployed += 1

    # Deploy TFLite Model
    if mode in ("tflite_bundle", "all") and SOURCE_TFLITE.is_file():
        dest = dest_dir / "safety_model_int8.tflite"
        shutil.copy2(SOURCE_TFLITE, dest)
        print(f"  [✓] TFLite Model      -> {dest}")
        deployed += 1

    # Deploy Normalization Stats
    if mode in ("tflite_bundle", "all") and SOURCE_STATS.is_file():
        dest = dest_dir / "normalization_stats.json"
        shutil.copy2(SOURCE_STATS, dest)
        print(f"  [✓] Normalization JSON -> {dest}")
        deployed += 1

    if deployed == 0:
        print(f"[!] Target mode was '{mode}', but the corresponding files were not in artifacts/.")
        sys.exit(1)

    print("\n✅ Deployment finished successfully!\n")


if __name__ == "__main__":
    main()