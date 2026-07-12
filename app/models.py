import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Element(str, enum.Enum):
    fire = "fire"
    ice = "ice"
    storm = "storm"
    earth = "earth"
    shadow = "shadow"


class Rank(str, enum.Enum):
    novice = "novice"
    adept = "adept"
    master = "master"
    archon = "archon"


class QuestStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Rider(Base):
    __tablename__ = "riders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    rank: Mapped[Rank] = mapped_column(Enum(Rank), default=Rank.novice)
    guild: Mapped[str] = mapped_column(String(100), default="Вольные крылья")
    victories: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    dragons: Mapped[list["Dragon"]] = relationship(back_populates="rider")
    quests: Mapped[list["Quest"]] = relationship(back_populates="assigned_rider")


class Dragon(Base):
    __tablename__ = "dragons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    element: Mapped[Element] = mapped_column(Enum(Element))
    color: Mapped[str] = mapped_column(String(50))
    age_years: Mapped[int] = mapped_column(Integer, default=1)
    danger_level: Mapped[int] = mapped_column(Integer, default=1)  # 1..10
    tamed: Mapped[bool] = mapped_column(Boolean, default=False)
    rider_id: Mapped[int | None] = mapped_column(ForeignKey("riders.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    rider: Mapped[Rider | None] = relationship(back_populates="dragons")


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1..10
    reward_gold: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[QuestStatus] = mapped_column(Enum(QuestStatus), default=QuestStatus.open)
    assigned_rider_id: Mapped[int | None] = mapped_column(ForeignKey("riders.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    assigned_rider: Mapped[Rider | None] = relationship(back_populates="quests")
