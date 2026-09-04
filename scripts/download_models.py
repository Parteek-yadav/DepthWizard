#!/usr/bin/env python3
"""
DepthWizard — Depth Anything V2 ONNX Model Downloader

Downloads the pre-converted Depth Anything V2 Small (ViT-S) ONNX model
from the onnx-community Hugging Face repository into backend/cache/.

Usage:
    python scripts/download_models.py

The model is licensed under Apache 2.0 (same as the original Depth Anything V2).
Source: https://huggingface.co/onnx-community/depth-anything-v2-small
"""

import hashlib
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_URL = (
    "https://huggingface.co/onnx-community/depth-anything-v2-small"
    "/resolve/main/onnx/model.onnx"
)
MODEL_FILENAME = "depth_anything_v2_vits.onnx"
EXPECTED_MIN_SIZE_BYTES = 90_000_000  # ~90 MB minimum sanity check

# Resolve paths relative to repo root (scripts/ is one level below root)
REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / "backend" / "cache"
MODEL_PATH = CACHE_DIR / MODEL_FILENAME


def sha256_file(filepath: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    if size_bytes >= 1 << 30:
        return f"{size_bytes / (1 << 30):.2f} GB"
    if size_bytes >= 1 << 20:
        return f"{size_bytes / (1 << 20):.1f} MB"
    if size_bytes >= 1 << 10:
        return f"{size_bytes / (1 << 10):.1f} KB"
    return f"{size_bytes} B"


def download_model() -> bool:
    """Download the ONNX model. Returns True on success."""
    try:
        import requests
    except ImportError:
        print("ERROR: 'requests' package not installed.")
        print("       Run: pip install requests")
        return False

    # Idempotent: skip if file already exists and looks valid
    if MODEL_PATH.exists():
        size = MODEL_PATH.stat().st_size
        if size >= EXPECTED_MIN_SIZE_BYTES:
            digest = sha256_file(MODEL_PATH)
            print(f"[OK] Model already exists: {MODEL_PATH}")
            print(f"   Size:   {format_size(size)}")
            print(f"   SHA256: {digest}")
            print("   Skipping download (file already present and valid).")
            return True
        else:
            print(f"[WARN] Existing file too small ({format_size(size)}), re-downloading...")
            MODEL_PATH.unlink()

    # Ensure cache directory exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("  DepthWizard -- Downloading Depth Anything V2 Small (ONNX)")
    print("=" * 65)
    print(f"  Source:  onnx-community/depth-anything-v2-small")
    print(f"  License: Apache 2.0")
    print(f"  Target:  {MODEL_PATH}")
    print()

    tmp_path = MODEL_PATH.with_suffix(".onnx.tmp")
    start_time = time.time()

    try:
        with requests.get(MODEL_URL, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(tmp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1 << 20):  # 1 MB chunks
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded / total * 100
                        bar_len = 40
                        filled = int(bar_len * downloaded / total)
                        bar = "#" * filled + "-" * (bar_len - filled)
                        print(
                            f"\r  Downloading: [{bar}] {pct:5.1f}%  "
                            f"({format_size(downloaded)} / {format_size(total)})",
                            end="", flush=True,
                        )
            print()  # newline after progress bar

    except requests.exceptions.RequestException as e:
        print(f"\n[FAIL] Download failed: {e}")
        if tmp_path.exists():
            tmp_path.unlink()
        return False

    elapsed = time.time() - start_time

    # Validate downloaded file
    if not tmp_path.exists() or tmp_path.stat().st_size < EXPECTED_MIN_SIZE_BYTES:
        print(f"[FAIL] Downloaded file is too small or missing. Expected >={format_size(EXPECTED_MIN_SIZE_BYTES)}.")
        if tmp_path.exists():
            tmp_path.unlink()
        return False

    # Rename tmp -> final
    tmp_path.rename(MODEL_PATH)

    size = MODEL_PATH.stat().st_size
    digest = sha256_file(MODEL_PATH)

    print()
    print(f"  [OK] Download complete in {elapsed:.1f}s")
    print(f"     File:   {MODEL_PATH}")
    print(f"     Size:   {format_size(size)}")
    print(f"     SHA256: {digest}")
    print()

    # Quick ONNX load validation
    try:
        import onnxruntime as ort
        sess = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
        inp = sess.get_inputs()[0]
        out = sess.get_outputs()[0]
        print(f"  [OK] ONNX Runtime validation passed")
        print(f"     Input:  {inp.name} {inp.shape} ({inp.type})")
        print(f"     Output: {out.name} {out.shape} ({out.type})")
    except Exception as e:
        print(f"  [WARN] ONNX validation warning: {e}")
        print(f"     The file was downloaded but could not be loaded by onnxruntime.")

    print()
    print("=" * 65)
    print("  Model ready. You can now start DepthWizard with real inference.")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
