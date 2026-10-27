"""Prepare fixed shell assets from canonical originals, never visitor choices."""

from pathlib import Path
import shutil


def prepare_assets():
    studio = Path(__file__).resolve().parent
    source = studio.parent / "financial/static"
    destination = studio / "static"
    destination.mkdir(exist_ok=True)
    for path in source.iterdir():
        if path.suffix in {".ttf", ".txt"}:
            shutil.copyfile(path, destination / path.name)


if __name__ == "__main__":
    prepare_assets()
