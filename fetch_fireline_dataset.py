"""
Download dataset Fireline_Datasets dari Hugging Face.

Struktur repository Hugging Face:
    data/
    ├── additions/
    └── raw/

Struktur lokal setelah download:
    data/
    ├── additions/
    └── raw/

Contoh:
    python fetch_fireline_dataset.py

Atau custom output:
    python fetch_fireline_dataset.py --output dataset

Untuk dataset private/gated, login terlebih dahulu:
    hf auth login

atau gunakan environment variable:
    HF_TOKEN
"""

from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import snapshot_download


DATASET_ID = "inaka06/Fireline_Datasets"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Fireline_Datasets dari Hugging Face"
    )

    parser.add_argument(
        "--output",
        default="data",
        help="Folder output dataset (default: data)",
    )

    parser.add_argument(
        "--token",
        default=None,
        help="HF token; alternatifnya gunakan HF_TOKEN",
    )

    return parser.parse_args()


def fetch_dataset(output: str | Path = "data", token: str | None = None) -> Path:
    """Download the dataset and return the local output directory."""
    output_dir = Path(output)
    token = token or os.getenv("HF_TOKEN")
    print("=" * 60)
    print("       Fireline Datasets Downloader")
    print("=" * 60)

    print(f"\nDataset : {DATASET_ID}")
    print(f"Output  : {output_dir.resolve()}")

    # ---------------------------------------------------------
    # 1. Download repository dari Hugging Face
    # ---------------------------------------------------------

    print("\n[1/3] Mengunduh dataset dari Hugging Face...")
    print("      Progress bar akan muncul di bawah.\n")

    with tempfile.TemporaryDirectory() as temp_dir:

        snapshot_dir = Path(
            snapshot_download(
                repo_id=DATASET_ID,
                repo_type="dataset",
                token=token,
                local_dir=temp_dir,
            )
        )

        # Repository HF memiliki struktur:
        #
        # data/
        # ├── additions/
        # └── raw/
        #
        # Kita hanya mengambil ISI folder data tersebut.

        source_dir = snapshot_dir / "data"

        if not source_dir.exists():
            raise FileNotFoundError(
                "Folder 'data' tidak ditemukan di repository Hugging Face.\n"
                f"Repository: {DATASET_ID}"
            )

        # ---------------------------------------------------------
        # 2. Copy isi data/ dari HF ke data/ lokal
        # ---------------------------------------------------------

        print("\n[2/3] Menyalin file ke folder output...")

        output_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():

            destination = output_dir / item.name

            # Kalau folder/file sudah ada, hapus dulu
            if destination.exists():
                if destination.is_dir():
                    shutil.rmtree(destination)
                else:
                    destination.unlink()

            # Copy folder
            if item.is_dir():
                shutil.copytree(item, destination)

            # Copy file
            else:
                shutil.copy2(item, destination)

    # ---------------------------------------------------------
    # 3. Tampilkan hasil
    # ---------------------------------------------------------

    print("\n[3/3] Download selesai!")

    print(f"\nDataset disimpan di:")
    print(f"  {output_dir.resolve()}")

    print("\nStruktur dataset:")

    for path in sorted(output_dir.rglob("*")):

        relative_path = path.relative_to(output_dir)

        if path.is_dir():
            print(f"  [DIR]  {relative_path}")

        else:
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"  [FILE] {relative_path} ({size_mb:.2f} MB)")

    print("\nSelesai!")
    return output_dir


def main() -> None:
    args = parse_args()
    fetch_dataset(args.output, args.token)


if __name__ == "__main__":
    main()
