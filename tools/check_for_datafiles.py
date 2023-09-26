"""FUNCTION TO CHECK FOR DATA FILES IN NON-WHITELISTED FOLDERS."""
import glob
from pathlib import Path

file_extensions = [
    "csv",
    "xlsx",
    "xls",
    "parquet",
    "tsv",
    "hdf5",
    "h5",
    "pickle",
    "pkl",
    "db",
    "sqlite",
    "sqlite3",
    "orc",
]
whitelist_folders = ["/venv"]  # starting from project root dir


def check_for_data_files():
    """Recursively finds all data files in non-whitelisted folders.

    Raises:
        AssertionError if data files are present in non-whitelisted folders.
    """
    project_dir = str(Path(__file__).parent.parent)
    whitelist_dir = {f"{project_dir}{dir}" for dir in whitelist_folders}

    found_files = {file for ext in file_extensions for file in glob.glob(project_dir + f"/**/*.{ext}", recursive=True)}
    whitelisted_files = {files for dir in whitelist_dir for files in found_files if files.startswith(dir)}
    to_be_removed_files = found_files - whitelisted_files

    assert (
        len(to_be_removed_files) == 0
    ), f"Caution! Please remove your data files {to_be_removed_files} before merging!"


if __name__ == "__main__":
    check_for_data_files()
