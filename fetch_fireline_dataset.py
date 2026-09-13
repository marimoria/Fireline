"""Download the shared FIRELINE dataset bundle from Hugging Face.

The bundle contains the raw FIRMS observations, BIG boundaries, school
reference data, and optional additions used by the kabupaten/kota drill-down.
This is an explicit opt-in helper; the normal pipeline never downloads data.
"""
from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import snapshot_download


DATASET_ID = "inaka06/Fireline_Datasets"


def fetch_dataset(output: str | Path = "data", token: str | None = None) -> Path:
    destination = Path(output)
    token = token or os.getenv("HF_TOKEN")
    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(snapshot_download(DATASET_ID, repo_type="dataset", token=token, local_dir=tmp))
        source = snapshot / "data"
        if not source.is_dir():
            raise FileNotFoundError(f"Folder data/ tidak ditemukan di {DATASET_ID}")
        destination.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            target = destination / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.copytree(item, target) if item.is_dir() else shutil.copy2(item, target)
    print(f"Dataset disimpan di {destination.resolve()}")
    for path in sorted(destination.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(destination)} ({path.stat().st_size / 1_048_576:.2f} MB)")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Ambil bundle dataset FIRELINE secara eksplisit")
    parser.add_argument("--output", default="data", help="Folder tujuan (default: data)")
    parser.add_argument("--token", default=None, help="Token HF; atau gunakan HF_TOKEN")
    args = parser.parse_args()
    fetch_dataset(args.output, args.token)


if __name__ == "__main__":
    main()
