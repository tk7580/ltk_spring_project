from sqlalchemy import (
    Column, BigInteger, Integer, SmallInteger, Boolean, String,
    Date, DateTime, DECIMAL, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# ───────────────────────────────────────────
class Series(Base):
    __tablename__ = "series"

    id            = Column(BigInteger, primary_key=True)
    regDate       = Column(DateTime, default=datetime.utcnow, nullable=False)
    updateDate    = Column(DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)
    titleKr       = Column(String(255))
    titleOriginal = Column(String(255))
    description   = Column(Text)
    thumbnailUrl  = Column(String(255))
    coverImageUrl = Column(String(255))
    author        = Column(String(100))
    publisher     = Column(String(100))
    studios       = Column(String(255))

# ───────────────────────────────────────────
class Work(Base):
    __tablename__ = "work"

    id               = Column(BigInteger, primary_key=True)
    seriesId         = Column(BigInteger, ForeignKey("series.id", ondelete="SET NULL"))
    anilistId        = Column(BigInteger, unique=True)
    regDate          = Column(DateTime, default=datetime.utcnow, nullable=False)
    updateDate       = Column(DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow, nullable=False)
    titleKr          = Column(String(255))
    titleOriginal    = Column(String(255))
    isOriginal       = Column(Boolean, default=False, nullable=False)
    releaseDate      = Column(Date)
    watchedCount     = Column(Integer, default=0, nullable=False)
    averageRating    = Column(DECIMAL(4, 2), default=0, nullable=False)
    ratingCount      = Column(Integer, default=0, nullable=False)
    episodes         = Column(Integer)
    duration         = Column(Integer)
    creators         = Column(String(255))
    studios          = Column(String(255))
    releaseSequence  = Column(Integer)
    timelineSequence = Column(Integer)
    isCompleted      = Column(Boolean, default=False, nullable=False)
    description      = Column(Text)
    thumbnailUrl     = Column(String(255))
    trailerUrl       = Column(String(255))

    series = relationship("Series", backref="works")

# ───────────────────────────────────────────
class WorkType(Base):
    __tablename__ = "workType"

    id         = Column(BigInteger, primary_key=True)
    regDate    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updateDate = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)
    name       = Column(String(50), unique=True, nullable=False)

class WorkTypeMapping(Base):
    __tablename__ = "workTypeMapping"
    __table_args__ = (UniqueConstraint("workId", "typeId", name="UK_workType"),)

    id      = Column(BigInteger, primary_key=True)
    regDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    workId  = Column(BigInteger, ForeignKey("work.id", ondelete="CASCADE"), nullable=False)
    typeId  = Column(BigInteger, ForeignKey("workType.id", ondelete="CASCADE"), nullable=False)

class WorkIdentifier(Base):
    __tablename__ = "workIdentifier"
    __table_args__ = (UniqueConstraint("sourceName", "sourceId", name="UK_source"),)

    id         = Column(BigInteger, primary_key=True)
    regDate    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updateDate = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)
    workId     = Column(BigInteger, ForeignKey("work.id", ondelete="CASCADE"), nullable=False)
    sourceName = Column(String(50), nullable=False)
    sourceId   = Column(String(255), nullable=False)

class Genre(Base):
    __tablename__ = "genre"

    id         = Column(BigInteger, primary_key=True)
    regDate    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updateDate = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)
    name       = Column(String(50), unique=True, nullable=False)

class WorkGenre(Base):
    __tablename__ = "workGenre"
    __table_args__ = (UniqueConstraint("workId", "genreId", name="UK_workGenre"),)

    id       = Column(BigInteger, primary_key=True)
    regDate  = Column(DateTime, default=datetime.utcnow, nullable=False)
    workId   = Column(BigInteger, ForeignKey("work.id", ondelete="CASCADE"), nullable=False)
    genreId  = Column(BigInteger, ForeignKey("genre.id", ondelete="CASCADE"), nullable=False)
