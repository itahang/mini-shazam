from sqlalchemy import String, Float, ForeignKey, BigInteger, Integer, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column("artistid", primary_key=True)
    name: Mapped[str] = mapped_column("name", String(100), nullable=False)

    songs: Mapped[list["Song"]] = relationship(back_populates="artist")


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column("songid", primary_key=True)
    artist_id: Mapped[int | None] = mapped_column(
        "artistid",
        ForeignKey("artist.artistid", ondelete="CASCADE"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column("title", String(200), nullable=False)
    album: Mapped[str | None] = mapped_column("albumname", String(200))
    duration: Mapped[float | None] = mapped_column("duration", Float)

    artist: Mapped[Artist | None] = relationship(back_populates="songs")
    fingerprints: Mapped[list["FingerPrint"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class FingerPrint(Base):
    __tablename__ = "fingerprint"

    fingerprint: Mapped[int] = mapped_column("fingerprint", BigInteger, primary_key=True)
    song_id: Mapped[int] = mapped_column(
        "songid",
        ForeignKey("songs.songid", ondelete="CASCADE"),
        primary_key=True,
    )
    anchor_frame: Mapped[int] = mapped_column("anchorframe", Integer, primary_key=True)

    song: Mapped[Song] = relationship(back_populates="fingerprints")

    __table_args__ = (Index("idx_fingerprint_hash", "fingerprint"),)