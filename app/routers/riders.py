from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.models import Rider, Rank, User
from app.security import get_current_user

router = APIRouter(prefix="/riders", tags=["Всадники"])


def _get_or_404(db: Session, rider_id: int) -> Rider:
    rider = db.get(Rider, rider_id)
    if rider is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Всадник id={rider_id} не найден")
    return rider


@router.get("", response_model=schemas.RiderPage, summary="Список всадников")
def list_riders(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    rank: Rank | None = Query(None, description="Фильтр по рангу"),
    search: str | None = Query(None, description="Поиск по имени"),
):
    query = db.query(Rider)
    if rank is not None:
        query = query.filter(Rider.rank == rank)
    if search:
        query = query.filter(Rider.name.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Rider.id).offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/{rider_id}", response_model=schemas.RiderOut, summary="Всадник по id")
def get_rider(rider_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, rider_id)


@router.get(
    "/{rider_id}/dragons",
    response_model=list[schemas.DragonOut],
    summary="Драконы всадника",
)
def rider_dragons(rider_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, rider_id).dragons


@router.post(
    "",
    response_model=schemas.RiderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать всадника (требует Bearer-токен)",
)
def create_rider(
    payload: schemas.RiderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rider = Rider(**payload.model_dump())
    db.add(rider)
    db.commit()
    db.refresh(rider)
    return rider


@router.patch(
    "/{rider_id}",
    response_model=schemas.RiderOut,
    summary="Частично обновить всадника (требует Bearer-токен)",
)
def update_rider(
    rider_id: int,
    payload: schemas.RiderUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rider = _get_or_404(db, rider_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rider, field, value)
    db.commit()
    db.refresh(rider)
    return rider


@router.delete(
    "/{rider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить всадника (требует Bearer-токен)",
)
def delete_rider(
    rider_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rider = _get_or_404(db, rider_id)
    if rider.dragons:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Нельзя удалить всадника, у которого есть драконы — сначала отвяжите их",
        )
    db.delete(rider)
    db.commit()
