from mini_shazam import utils
from mini_shazam.models import *
from pathlib import Path
from tinytag import TinyTag,TinyTagException
import os
import numpy as np
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

url = URL.create(
    "postgresql+psycopg",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="localhost",
    port=5432,
    database=os.getenv("POSTGRES_DB"),
)

engine = create_engine(url)


engine = create_engine(url)

Base.metadata.create_all(engine)



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
    
        tag = TinyTag.get(file_path)
        return {
            "title": tag.title,
            "artist": tag.artist,
            "album": tag.album,
            "duration": tag.duration,
        }
   



def main():
    song_path = Path("songs")
    save_dir.mkdir(parents=True, exist_ok=True)

    with Session(engine) as session:
        for item in song_path.rglob("*"):
            if not item.is_file() or not is_valid_song(item):
                continue

            print(f"Hashing: {item.name}")

            metadata = get_metainfo(item)
            fp = utils.fingerprint(item, ALPHA)

            artist_name = metadata["artist"] or "unknown"
            artist = session.query(Artist).filter_by(name=artist_name).first()
            if artist is None:
                artist = Artist(name=artist_name)

            song = Song(
                title=metadata["title"] or item.stem,
                album=metadata["album"],
                duration=metadata["duration"],
                artist=artist,
            )
            song.fingerprints = [
                FingerPrint(fingerprint=int(h), anchor_frame=int(a))
                for h, a in fp
            ]
            session.add(song)   # cascades to artist and fingerprints
            session.commit()

if __name__ == "__main__":

    main()
