from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import Element, QuestStatus, Rank

# ---------- Auth / Users ----------


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, examples=["ikkar"])
    email: EmailStr = Field(examples=["ikkar@academy.sky"])
    password: str = Field(min_length=6, max_length=128, examples=["wing-storm-42"])


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Riders ----------


class RiderBase(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Иккар Буревой"])
    rank: Rank = Rank.novice
    guild: str = Field(default="Вольные крылья", max_length=100)
    victories: int = Field(default=0, ge=0)


class RiderCreate(RiderBase):
    pass


class RiderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    rank: Rank | None = None
    guild: str | None = Field(default=None, max_length=100)
    victories: int | None = Field(default=None, ge=0)


class RiderOut(RiderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------- Dragons ----------


class DragonBase(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Эмберклык"])
    element: Element = Field(examples=[Element.fire])
    color: str = Field(max_length=50, examples=["алый"])
    age_years: int = Field(default=1, ge=0, le=5000)
    danger_level: int = Field(default=1, ge=1, le=10)
    tamed: bool = False
    rider_id: int | None = None


class DragonCreate(DragonBase):
    pass


class DragonUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    element: Element | None = None
    color: str | None = Field(default=None, max_length=50)
    age_years: int | None = Field(default=None, ge=0, le=5000)
    danger_level: int | None = Field(default=None, ge=1, le=10)
    tamed: bool | None = None
    rider_id: int | None = None


class DragonOut(DragonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------- Quests ----------


class QuestBase(BaseModel):
    title: str = Field(min_length=1, max_length=200, examples=["Найти гнездо грозового дракона"])
    description: str = ""
    difficulty: int = Field(default=1, ge=1, le=10)
    reward_gold: int = Field(default=100, ge=0)
    status: QuestStatus = QuestStatus.open
    assigned_rider_id: int | None = None


class QuestCreate(QuestBase):
    pass


class QuestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=10)
    reward_gold: int | None = Field(default=None, ge=0)
    status: QuestStatus | None = None
    assigned_rider_id: int | None = None


class QuestOut(QuestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------- Общее ----------


class Page(BaseModel):
    """Метаданные пагинации + элементы страницы."""

    total: int
    limit: int
    offset: int
    items: list


class DragonPage(Page):
    items: list[DragonOut]


class RiderPage(Page):
    items: list[RiderOut]


class QuestPage(Page):
    items: list[QuestOut]


class Message(BaseModel):
    detail: str
