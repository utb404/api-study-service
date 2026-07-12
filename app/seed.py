"""Начальные данные Академии: демо-пользователь, всадники, драконы, квесты."""
from sqlalchemy.orm import Session

from app.models import Dragon, Element, Quest, QuestStatus, Rank, Rider, User
from app.security import hash_password

DEMO_USER = {"username": "demo", "email": "demo@academy.sky", "password": "demo1234"}


def seed(db: Session) -> None:
    if db.query(User).first() is not None:
        return  # база уже наполнена

    db.add(
        User(
            username=DEMO_USER["username"],
            email=DEMO_USER["email"],
            hashed_password=hash_password(DEMO_USER["password"]),
        )
    )

    riders = [
        Rider(name="Иккар Буревой", rank=Rank.master, guild="Орден Грозы", victories=42),
        Rider(name="Сельвина Пепел", rank=Rank.archon, guild="Пепельный круг", victories=97),
        Rider(name="Тобб Крепкорук", rank=Rank.novice, guild="Вольные крылья", victories=2),
        Rider(name="Мира Ледяная Игла", rank=Rank.adept, guild="Северный шпиль", victories=18),
    ]
    db.add_all(riders)
    db.flush()

    dragons = [
        Dragon(name="Эмберклык", element=Element.fire, color="алый",
               age_years=120, danger_level=8, tamed=True, rider_id=riders[1].id),
        Dragon(name="Вьюжник", element=Element.ice, color="серебристо-белый",
               age_years=45, danger_level=5, tamed=True, rider_id=riders[3].id),
        Dragon(name="Громовержец", element=Element.storm, color="сине-стальной",
               age_years=300, danger_level=10, tamed=False),
        Dragon(name="Мохоспин", element=Element.earth, color="изумрудный",
               age_years=15, danger_level=2, tamed=True, rider_id=riders[2].id),
        Dragon(name="Тенекрыл", element=Element.shadow, color="чёрный",
               age_years=666, danger_level=9, tamed=False),
        Dragon(name="Искорка", element=Element.fire, color="золотистый",
               age_years=3, danger_level=1, tamed=True, rider_id=riders[0].id),
    ]
    db.add_all(dragons)

    quests = [
        Quest(title="Найти гнездо Громовержца",
              description="Разведать грозовые пики и нанести гнездо на карту.",
              difficulty=9, reward_gold=5000, status=QuestStatus.open),
        Quest(title="Доставить лекарство в Северный шпиль",
              description="Перелёт через ледяной каньон, груз хрупкий.",
              difficulty=4, reward_gold=800, status=QuestStatus.in_progress,
              assigned_rider_id=riders[3].id),
        Quest(title="Приручить Тенекрыла",
              description="Легенды говорят, что он слушает только тех, кто не боится темноты.",
              difficulty=10, reward_gold=12000, status=QuestStatus.open),
        Quest(title="Сопроводить караван торговцев",
              description="Обычное патрулирование над торговым трактом.",
              difficulty=2, reward_gold=300, status=QuestStatus.completed,
              assigned_rider_id=riders[0].id),
    ]
    db.add_all(quests)
    db.commit()
