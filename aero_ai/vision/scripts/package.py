#!/usr/bin/env python3
"""
Interactive export script for ResQVision Vision models.
Asks the user where to deploy exported ONNX artifacts.
"""

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parents[1]  # ResQVision repo root
ARTIFACTS_DIR = ROOT / "artifacts"

SOURCE_ONNX = ARTIFACTS_DIR / "aero_detector.onnx"
SOURCE_META = ARTIFACTS_DIR / "aero_detector.json"


def select_destination() -> Path:
    # Preset sensible targets relative to workspace
    targets = {
        "1": ("aero_cloud server (artifacts/models)", WORKSPACE_ROOT / "aero_cloud" / "artifacts" / "models"),
        "2": ("Local distribution archive (vision/dist)", ROOT / "dist"),
    }

    print("\n" + "=" * 60)
    print("📦 ResQVision Vision Artifact Deployment")
    print("=" * 60)
    print("Select where to deploy the trained ONNX model:\n")

    for key, (name, path) in targets.items():
        exists_mark = " [found]" if path.parent.exists() else ""
        print(f"  [{key}] {name}{exists_mark}")
        print(f"      -> {path}")

    print("  [3] Enter a custom directory path")
    print("  [q] Cancel")

    while True:
        choice = input("\nEnter choice [1-3 / q] (default: 1): ").strip().lower() or "1"

        if choice in ("q", "quit", "exit"):
            print("\n[!] Deployment cancelled.")
            sys.exit(0)

        if choice in targets:
            selected_path = targets[choice][1]
            break
        elif choice == "4":
            custom_path_str = input("Enter destination path: ").strip()
            if not custom_path_str:
                print("Path cannot be empty. Try again.")
                continue
            selected_path = Path(custom_path_str).expanduser().resolve()
            break
        else:
            print("Invalid choice. Please choose 1, 2, 3, or q.")

    confirm = input(f"\nDeploy artifacts to:\n  {selected_path}\nProceed? [Y/n]: ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("[!] Aborted by user.")
        sys.exit(0)

    return selected_path


def main():
    if not SOURCE_ONNX.is_file():
        print(f"\n❌ [ERROR] Model artifact missing: {SOURCE_ONNX}")
        print("Run 'python scripts/build.py' or 'aero-ai export' first.")
        sys.exit(1)

    dest_dir = select_destination()
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("\n[*] Copying artifacts...")
    dest_onnx = dest_dir / "aero_detector.onnx"
    shutil.copy2(SOURCE_ONNX, dest_onnx)
    print(f"  [✓] ONNX Model  -> {dest_onnx}")

    if SOURCE_META.is_file():
        dest_meta = dest_dir / "aero_detector.json"
        shutil.copy2(SOURCE_META, dest_meta)
        print(f"  [✓] Metadata    -> {dest_meta}")

    print("\n✅ Deployment finished successfully!\n")


if __name__ == "__main__":
    main()