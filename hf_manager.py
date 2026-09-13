import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download, snapshot_download, create_repo
from huggingface_hub.errors import RepositoryNotFoundError

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO_TYPE = "dataset"
HF_REPO_ID = ""
DATA_DIR: Path = None

def setup_session():
    global HF_REPO_ID, DATA_DIR
    
    repo = input("Enter HuggingFace Repository ID: ").strip()
    while not repo:
        repo = input("Repository ID cannot be empty. Enter HuggingFace Repository ID: ").strip()
    HF_REPO_ID = repo
    
    dir_path = input("Enter full path to local data directory: ").strip()
    while not dir_path:
        dir_path = input("Directory path cannot be empty. Enter full path to local data directory: ").strip()
    DATA_DIR = Path(dir_path)

def ensure_repo_exists(api: HfApi):
    try:
        api.repo_info(repo_id=HF_REPO_ID, repo_type=HF_REPO_TYPE, token=HF_TOKEN)
    except RepositoryNotFoundError:
        create_repo(
            repo_id=HF_REPO_ID,
            repo_type=HF_REPO_TYPE,
            private=False,
            token=HF_TOKEN,
        )

def collect_all_files(directory: Path) -> list[Path]:
    return sorted([f for f in directory.rglob("*") if f.is_file()])

def pick_files(all_files: list[Path]) -> list[Path]:
    if not all_files:
        return []

    for i, f in enumerate(all_files, 1):
        rel = f.relative_to(DATA_DIR)
        size_kb = f.stat().st_size / 1024
        print(f"[{i}] {rel} ({size_kb:.1f} KB)")

    choice = input("Enter file numbers to select (e.g. 1 2 3), or 'all': ").strip().lower()

    if choice == "all":
        return all_files
    else:
        try:
            indices = [int(val) - 1 for val in choice.split()]
            return [all_files[i] for i in indices]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return []

def upload_files(api: HfApi, selected_files: list[Path]):
    ensure_repo_exists(api)
    rel_paths = [str(f.relative_to(DATA_DIR)).replace("\\", "/") for f in selected_files]
    try:
        api.upload_large_folder(
            folder_path=str(DATA_DIR),
            repo_id=HF_REPO_ID,
            repo_type=HF_REPO_TYPE,
            allow_patterns=rel_paths,
        )
    except Exception as e:
        print(f"Upload failed: {e}")

def list_local_files():
    if not DATA_DIR.exists():
        print("Directory not found.")
        return

    all_files = collect_all_files(DATA_DIR)
    if not all_files:
        print("No files found.")
        return

    total_kb = 0
    for f in all_files:
        rel = f.relative_to(DATA_DIR)
        size_kb = f.stat().st_size / 1024
        total_kb += size_kb
        print(f"{rel} ({size_kb:.1f} KB)")
    print(f"Total: {len(all_files)} files ({total_kb / 1024:.1f} MB)")

def upload_local_files():
    if not DATA_DIR.exists():
        print("Directory not found.")
        return

    all_files = collect_all_files(DATA_DIR)
    selected = pick_files(all_files)
    if not selected:
        return

    api = HfApi(token=HF_TOKEN)
    upload_files(api, selected)

def download_all_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=HF_REPO_ID,
        repo_type=HF_REPO_TYPE,
        local_dir=str(DATA_DIR),
        token=HF_TOKEN,
    )

def download_specific_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw = input("Enter filename(s) as they appear in the repo (separated by space): ").strip()
    filenames = raw.split()

    if not filenames:
        return

    for filename in filenames:
        try:
            hf_hub_download(
                repo_id=HF_REPO_ID,
                filename=filename,
                repo_type=HF_REPO_TYPE,
                token=HF_TOKEN,
                local_dir=str(DATA_DIR),
            )
        except Exception as e:
            print(f"Failed: {filename} - {e}")

def main():
    setup_session()

    while True:
        print(f"\nActive Repo: {HF_REPO_ID}")
        print(f"Active Dir: {DATA_DIR}")
        print("1. List local files")
        print("2. Upload local files to HuggingFace")
        print("3. Download ALL files from HuggingFace")
        print("4. Download specific file(s) from HuggingFace")
        print("5. Change Repository and Directory")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            sys.exit(0)
        elif choice == "1":
            list_local_files()
        elif choice == "2":
            upload_local_files()
        elif choice == "3":
            download_all_files()
        elif choice == "4":
            download_specific_files()
        elif choice == "5":
            setup_session()
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
