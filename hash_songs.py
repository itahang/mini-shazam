from mini_shazam import utils
from pathlib import Path
from tinytag import TinyTag,TinyTagException
import os
import numpy as np

ALPHA=0.2
save_dir = Path(os.path.join(os.curdir,"hashes"))

def is_valid_song(file_path):
    if not TinyTag.is_supported(file_path):
        return False

    try:
        tag = TinyTag.get(file_path)
        return tag.duration is not None and tag.duration > 0
    except TinyTagException:
        return False


def get_metainfo(file_path):
    try:
        tag = TinyTag.get(file_path)
        return {
            "filename": Path(tag.filename).name,
            "title": tag.title,
            "artist": tag.artist,
            "album": tag.album,
            "duration": tag.duration,
        }
    except TinyTagException:
        return None


def main():
    song_path = Path("songs")
    save_dir.mkdir(parents=True, exist_ok=True)

    for item in song_path.rglob("*"):
        if not item.is_file() or not is_valid_song(item):
            continue

        print(f"Hashing: {item.name}")

        metadata = get_metainfo(item)
        print(metadata)

        fp = utils.fingerprint(item, ALPHA)
        hashes_only = [h for h, _ in fp]


        # output_path = save_dir / f"{item.stem}.npy"
        # np.save(output_path, hashes_only)

        # print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()