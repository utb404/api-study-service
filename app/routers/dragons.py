from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.models import Dragon, Element, Rider, User
from app.security import get_current_user

router = APIRouter(prefix="/dragons", tags=["Драконы"])


def _get_or_404(db: Session, dragon_id: int) -> Dragon:
    dragon = db.get(Dragon, dragon_id)
    if dragon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Дракон id={dragon_id} не найден")
    return dragon


def _check_rider(db: Session, rider_id: int | None) -> None:
    if rider_id is not None and db.get(Rider, rider_id) is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, f"Всадник id={rider_id} не существует"
        )


@router.get("", response_model=schemas.DragonPage, summary="Список драконов (пагинация и фильтры)")
def list_dragons(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение"),
    element: Element | None = Query(None, description="Фильтр по стихии"),
    tamed: bool | None = Query(None, description="Только приручённые / дикие"),
    search: str | None = Query(None, description="Поиск по имени (подстрока)"),
):
    query = db.query(Dragon)
    if element is not None:
        query = query.filter(Dragon.element == element)
    if tamed is not None:
        query = query.filter(Dragon.tamed == tamed)
    if search:
        query = query.filter(Dragon.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Dragon.id).offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/{dragon_id}", response_model=schemas.DragonOut, summary="Дракон по id")
def get_dragon(dragon_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, dragon_id)


@router.post(
    "",
    response_model=schemas.DragonOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать дракона (требует Bearer-токен)",
)
def create_dragon(
    payload: schemas.DragonCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    _check_rider(db, payload.rider_id)
    dragon = Dragon(**payload.model_dump())
    db.add(dragon)
    db.commit()
    db.refresh(dragon)
    return dragon


@router.put(
    "/{dragon_id}",
    response_model=schemas.DragonOut,
    summary="Полностью заменить дракона (требует Bearer-токен)",
)
def replace_dragon(
    dragon_id: int,
    payload: schemas.DragonCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    dragon = _get_or_404(db, dragon_id)
    _check_rider(db, payload.rider_id)
    for field, value in payload.model_dump().items():
        setattr(dragon, field, value)
    db.commit()
    db.refresh(dragon)
    return dragon


@router.patch(
    "/{dragon_id}",
    response_model=schemas.DragonOut,
    summary="Частично обновить дракона (требует Bearer-токен)",
)
def update_dragon(
    dragon_id: int,
    payload: schemas.DragonUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    dragon = _get_or_404(db, dragon_id)
    updates = payload.model_dump(exclude_unset=True)
    if "rider_id" in updates:
        _check_rider(db, updates["rider_id"])
    for field, value in updates.items():
        setattr(dragon, field, value)
    db.commit()
    db.refresh(dragon)
    return dragon


@router.delete(
    "/{dragon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить дракона (требует Bearer-токен)",
)
def delete_dragon(
    dragon_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    dragon = _get_or_404(db, dragon_id)
    db.delete(dragon)
    db.commit()
