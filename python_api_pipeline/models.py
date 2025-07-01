"""Unified SQLAlchemy models (camelCase)."""
from datetime import datetime, date
from typing import List
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, Date, DateTime, Integer, BigInteger, DECIMAL, ForeignKey, UniqueConstraint

Base = declarative_base()

class TimestampMixin:
    regDate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updateDate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Series(Base, TimestampMixin):
    __tablename__ = "series"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    titleKr: Mapped[str | None] = mapped_column(String(255))
    titleOriginal: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    thumbnailUrl: Mapped[str | None] = mapped_column(String(255))
    coverImageUrl: Mapped[str | None] = mapped_column(String(255))
    author: Mapped[str | None] = mapped_column(String(100))
    publisher: Mapped[str | None] = mapped_column(String(100))
    studios: Mapped[str | None] = mapped_column(String(255))

    works: Mapped[List["Work"]] = relationship(back_populates="series", cascade="all, delete-orphan")

class Work(Base, TimestampMixin):
    __tablename__ = "work"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    seriesId: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("series.id", ondelete="SET NULL"))
    anilistId: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    titleKr: Mapped[str | None] = mapped_column(String(255))
    titleOriginal: Mapped[str | None] = mapped_column(String(255))
    isOriginal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    releaseDate: Mapped[date | None] = mapped_column(Date)
    watchedCount: Mapped[int] = mapped_column(Integer, default=0)
    averageRating: Mapped[float] = mapped_column(DECIMAL(4,2), default=0)
    ratingCount: Mapped[int] = mapped_column(Integer, default=0)
    episodes: Mapped[int | None] = mapped_column(Integer)
    duration: Mapped[int | None] = mapped_column(Integer)
    creators: Mapped[str | None] = mapped_column(String(255))
    studios: Mapped[str | None] = mapped_column(String(255))
    releaseSequence: Mapped[int | None] = mapped_column(Integer)
    timelineSequence: Mapped[int | None] = mapped_column(Integer)
    isCompleted: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    thumbnailUrl: Mapped[str | None] = mapped_column(String(255))
    trailerUrl: Mapped[str | None] = mapped_column(String(255))

    series: Mapped["Series | None"] = relationship(back_populates="works")
    identifiers: Mapped[List["WorkIdentifier"]] = relationship(back_populates="work", cascade="all, delete-orphan")
    types: Mapped[List["WorkTypeMapping"]] = relationship(back_populates="work", cascade="all, delete-orphan")

class WorkType(Base, TimestampMixin):
    __tablename__ = "work_type"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

class WorkTypeMapping(Base):
    __tablename__ = "work_type_mapping"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    regDate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    workId: Mapped[int] = mapped_column(BigInteger, ForeignKey("work.id", ondelete="CASCADE"))
    typeId: Mapped[int] = mapped_column(BigInteger, ForeignKey("work_type.id", ondelete="CASCADE"))

    work: Mapped["Work"] = relationship(back_populates="types")
    type: Mapped["WorkType"] = relationship()

    __table_args__ = (UniqueConstraint("workId", "typeId", name="UK_work_type"),)

class WorkIdentifier(Base, TimestampMixin):
    __tablename__ = "work_identifier"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workId: Mapped[int] = mapped_column(BigInteger, ForeignKey("work.id", ondelete="CASCADE"))
    sourceName: Mapped[str] = mapped_column(String(50))
    sourceId: Mapped[str] = mapped_column(String(255))

    work: Mapped["Work"] = relationship(back_populates="identifiers")

    __table_args__ = (UniqueConstraint("sourceName", "sourceId", name="UK_source"),)
