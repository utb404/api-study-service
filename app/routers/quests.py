from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.models import Quest, QuestStatus, Rider, User
from app.security import get_current_user, require_api_key

router = APIRouter(prefix="/quests", tags=["Квесты"])


def _get_or_404(db: Session, quest_id: int) -> Quest:
    quest = db.get(Quest, quest_id)
    if quest is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Квест id={quest_id} не найден")
    return quest


def _check_rider(db: Session, rider_id: int | None) -> None:
    if rider_id is not None and db.get(Rider, rider_id) is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, f"Всадник id={rider_id} не существует"
        )


@router.get("", response_model=schemas.QuestPage, summary="Список квестов")
def list_quests(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: QuestStatus | None = Query(
        None, alias="status", description="Фильтр по статусу"
    ),
    min_difficulty: int | None = Query(None, ge=1, le=10),
    max_difficulty: int | None = Query(None, ge=1, le=10),
):
    query = db.query(Quest)
    if status_filter is not None:
        query = query.filter(Quest.status == status_filter)
    if min_difficulty is not None:
        query = query.filter(Quest.difficulty >= min_difficulty)
    if max_difficulty is not None:
        query = query.filter(Quest.difficulty <= max_difficulty)
    total = query.count()
    items = query.order_by(Quest.id).offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/{quest_id}", response_model=schemas.QuestOut, summary="Квест по id")
def get_quest(quest_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, quest_id)


@router.post(
    "",
    response_model=schemas.QuestOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать квест (требует Bearer-токен)",
)
def create_quest(
    payload: schemas.QuestCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    _check_rider(db, payload.assigned_rider_id)
    quest = Quest(**payload.model_dump())
    db.add(quest)
    db.commit()
    db.refresh(quest)
    return quest


@router.patch(
    "/{quest_id}",
    response_model=schemas.QuestOut,
    summary="Частично обновить квест (требует Bearer-токен)",
)
def update_quest(
    quest_id: int,
    payload: schemas.QuestUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    quest = _get_or_404(db, quest_id)
    updates = payload.model_dump(exclude_unset=True)
    if "assigned_rider_id" in updates:
        _check_rider(db, updates["assigned_rider_id"])
    for field, value in updates.items():
        setattr(quest, field, value)
    db.commit()
    db.refresh(quest)
    return quest


@router.delete(
    "/{quest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить квест (требует заголовок X-API-Key)",
    description="Пример авторизации по API-ключу. "
    "Передайте заголовок `X-API-Key` (по умолчанию `sky-fire-9000`).",
)
def delete_quest(
    quest_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    quest = _get_or_404(db, quest_id)
    db.delete(quest)
    db.commit()
