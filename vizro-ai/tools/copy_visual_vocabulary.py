"""Copy the visual vocabulary JSON file from vizro-core to vizro-ai."""

import shutil
from pathlib import Path


def copy_visual_vocabulary():
    """Copy the visual vocabulary JSON file from vizro-core to vizro-ai."""
    source_dir = Path(__file__).parents[2] / "vizro-core" / "examples" / "visual-vocabulary"
    source_file = source_dir / "visual_vocabulary.json"

    if not source_file.exists():
        raise FileNotFoundError(
            f"Visual vocabulary JSON not found at {source_file}.\n"
            "Please run the generate_vivivo_json.py script in the "
            "vizro-core/examples/visual-vocabulary directory first."
        )

    target_dir = Path(__file__).parents[1] / "src" / "vizro_ai"
    target_file = target_dir / "visual_vocabulary.json"

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, target_file)


if __name__ == "__main__":
    copy_visual_vocabulary()
