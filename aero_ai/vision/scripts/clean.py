#!/usr/bin/env python3
"""
aero_ai/vision/scripts/clean.py

Cleans build caches, __pycache__, intermediate conversion files,
and optionally checkpoints, validation predictions, or artifacts.

Usage:
    python scripts/clean.py                     # Safe clean: caches & temp build dirs
    python scripts/clean.py --checkpoints       # Clean checkpoints/ (*.pt)
    python scripts/clean.py --artifacts         # Clean artifacts/ (*.onnx, evaluation.json)
    python scripts/clean.py --all               # Full cleanup
"""

import argparse
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def remove_path(path: Path):
    if not path.exists():
        return
    try:
        if path.is_file() or path.is_symlink():
            path.unlink()
            print(f"  [-] Removed file: {path.relative_to(PROJECT_ROOT)}")
        elif path.is_dir():
            shutil.rmtree(path)
            print(f"  [-] Removed directory: {path.relative_to(PROJECT_ROOT)}")
    except Exception as e:
        print(f"  [!] Failed to remove {path}: {e}")


def clean_python_cache():
    print("[*] Cleaning Python bytecode, __pycache__, and build directories...")
    for p in PROJECT_ROOT.rglob("__pycache__"):
        remove_path(p)
    for p in PROJECT_ROOT.rglob("*.py[cod]"):
        remove_path(p)

    for dirname in ["build", "dist", "*.egg-info", ".pytest_cache"]:
        for p in PROJECT_ROOT.glob(dirname):
            remove_path(p)
        for p in (PROJECT_ROOT / "src").glob(dirname):
            remove_path(p)


def clean_checkpoints():
    print("[*] Cleaning PyTorch model checkpoints (*.pt)...")
    checkpoints_dir = PROJECT_ROOT / "checkpoints"
    if checkpoints_dir.exists():
        for pt in checkpoints_dir.glob("*.pt"):
            remove_path(pt)


def clean_artifacts():
    print("[*] Cleaning generated artifacts (*.onnx, *.json)...")
    artifacts_dir = PROJECT_ROOT / "artifacts"
    if artifacts_dir.exists():
        for item in artifacts_dir.iterdir():
            if item.is_file():
                remove_path(item)


def main():
    parser = argparse.ArgumentParser(description="Clean ResQVision Vision Workspace")
    parser.add_argument("--all", action="store_true", help="Clean all caches, checkpoints, and artifacts")
    parser.add_argument("--checkpoints", action="store_true", help="Remove trained .pt checkpoints")
    parser.add_argument("--artifacts", action="store_true", help="Remove exported .onnx and report files")
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("🧹 Cleaning ResQVision Vision Workspace")
    print("=" * 55)

    clean_python_cache()

    if args.all or args.checkpoints:
        clean_checkpoints()

    if args.all or args.artifacts:
        clean_artifacts()

    print("=" * 55)
    print("✅ Cleanup complete!\n")


if __name__ == "__main__":
    main()