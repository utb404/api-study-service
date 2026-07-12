# 🐉 Dragon Academy API

Учебный сервис-песочница для тренировки работы с REST API — по мотивам
[futuramaapi](https://futuramaapi.com), но во вселенной **Академии драконьих
всадников**. Драконы, всадники и квесты — всё выдуманное, зато запросы настоящие.

Подходит для практики с curl, Postman, requests, axios и любыми другими HTTP-клиентами.

## Что можно потренировать

| Навык | Где |
|---|---|
| GET со списками, пагинацией (`limit`/`offset`), фильтрами и поиском | `/dragons`, `/riders`, `/quests` |
| Полный CRUD: POST, PUT, PATCH, DELETE | `/dragons`, `/riders`, `/quests` |
| JWT-авторизация (OAuth2 password flow, Bearer-токен) | `/auth/*` и все изменяющие запросы |
| Авторизация по API-ключу (заголовок `X-API-Key`) | `DELETE /quests/{id}` |
| Обработка ошибок: 401, 403, 404, 409, 422 | везде |
| Произвольные статус-коды, задержки, echo-запросы | `/sandbox/*` |

## Быстрый старт

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Или в Docker:

```bash
docker build -t dragon-academy-api .
docker run -p 8000:8000 dragon-academy-api
```

После запуска:

- Swagger UI (интерактивная документация): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI-схема: http://localhost:8000/openapi.json

При первом старте создаётся SQLite-база `academy.db` с демо-данными.
Чтобы начать с чистого листа — просто удалите этот файл.

## Демо-доступы

- Пользователь: **demo / demo1234**
- API-ключ: **sky-fire-9000** (заголовок `X-API-Key`)

## Примеры запросов

### Чтение — без авторизации

```bash
# Список драконов, вторая страница по 2 штуки
curl "http://localhost:8000/dragons?limit=2&offset=2"

# Только огненные и приручённые
curl "http://localhost:8000/dragons?element=fire&tamed=true"

# Поиск по имени
curl "http://localhost:8000/dragons?search=гром"

# Один дракон (несуществующий id вернёт 404)
curl "http://localhost:8000/dragons/1"

# Драконы конкретного всадника
curl "http://localhost:8000/riders/1/dragons"

# Открытые квесты сложностью от 9
curl "http://localhost:8000/quests?status=open&min_difficulty=9"
```

### Регистрация и получение JWT-токена

```bash
# Регистрация (вернёт 201; повторная — 409)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "rider1", "email": "rider1@academy.sky", "password": "secret123"}'

# Токен — OAuth2 password flow, тело form-urlencoded!
curl -X POST http://localhost:8000/auth/token \
  -d "username=demo&password=demo1234"

# Кто я (требует Bearer-токен, без него — 401)
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <ТОКЕН>"
```

В Swagger UI можно нажать кнопку **Authorize**, ввести demo/demo1234 —
и токен подставится во все запросы автоматически.

### Изменение данных — с Bearer-токеном

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -d "username=demo&password=demo1234" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# POST — создать дракона (201)
curl -X POST http://localhost:8000/dragons \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Новичок", "element": "ice", "color": "голубой", "danger_level": 2}'

# PATCH — частичное обновление
curl -X PATCH http://localhost:8000/dragons/7 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tamed": true}'

# PUT — полная замена
curl -X PUT http://localhost:8000/dragons/7 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Ветеран", "element": "ice", "color": "белый", "age_years": 10, "danger_level": 4, "tamed": true}'

# DELETE — удаление (204)
curl -X DELETE http://localhost:8000/dragons/7 \
  -H "Authorization: Bearer $TOKEN"
```

### Авторизация по API-ключу

```bash
# Без ключа или с неверным ключом — 403
curl -X DELETE http://localhost:8000/quests/4

# С верным ключом — 204
curl -X DELETE http://localhost:8000/quests/4 \
  -H "X-API-Key: sky-fire-9000"
```

### Песочница для отладки клиентов

```bash
# Любой статус-код: тренировка обработки ошибок
curl -i http://localhost:8000/sandbox/status/418
curl -i http://localhost:8000/sandbox/status/503

# Задержка ответа (до 10 секунд) — тест таймаутов
curl "http://localhost:8000/sandbox/delay/3"

# Echo — вернёт метод, заголовки, query-параметры и тело запроса
curl -X PUT "http://localhost:8000/sandbox/echo?foo=bar" \
  -H "X-Custom: hello" \
  -d '{"any": "payload"}'

# Ваши заголовки глазами сервера
curl http://localhost:8000/sandbox/headers

# Генератор драконьих имён
curl "http://localhost:8000/sandbox/random-dragon-name?count=5"
```

## Ресурсы API

### Драконы `/dragons`

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| GET | `/dragons` | — | Список: `limit`, `offset`, `element`, `tamed`, `search` |
| GET | `/dragons/{id}` | — | Один дракон |
| POST | `/dragons` | Bearer | Создать |
| PUT | `/dragons/{id}` | Bearer | Полностью заменить |
| PATCH | `/dragons/{id}` | Bearer | Частично обновить |
| DELETE | `/dragons/{id}` | Bearer | Удалить |

Стихии (`element`): `fire`, `ice`, `storm`, `earth`, `shadow`.

### Всадники `/riders`

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| GET | `/riders` | — | Список: `limit`, `offset`, `rank`, `search` |
| GET | `/riders/{id}` | — | Один всадник |
| GET | `/riders/{id}/dragons` | — | Драконы всадника |
| POST | `/riders` | Bearer | Создать |
| PATCH | `/riders/{id}` | Bearer | Обновить |
| DELETE | `/riders/{id}` | Bearer | Удалить (409, если есть драконы) |

Ранги (`rank`): `novice`, `adept`, `master`, `archon`.

### Квесты `/quests`

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| GET | `/quests` | — | Список: `limit`, `offset`, `status`, `min_difficulty`, `max_difficulty` |
| GET | `/quests/{id}` | — | Один квест |
| POST | `/quests` | Bearer | Создать |
| PATCH | `/quests/{id}` | Bearer | Обновить |
| DELETE | `/quests/{id}` | X-API-Key | Удалить |

Статусы (`status`): `open`, `in_progress`, `completed`.

### Авторизация `/auth`

| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/register` | Регистрация (JSON) |
| POST | `/auth/token` | Получить JWT (form-data: `username`, `password`) |
| GET | `/auth/me` | Текущий пользователь (Bearer) |

Токен живёт 60 минут (настраивается через `ACCESS_TOKEN_EXPIRE_MINUTES`).

## Конфигурация (переменные окружения)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `SECRET_KEY` | dev-значение | Ключ подписи JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Время жизни токена |
| `DATABASE_URL` | `sqlite:///./academy.db` | Строка подключения SQLAlchemy |
| `API_KEY` | `sky-fire-9000` | Значение заголовка `X-API-Key` |

## Тесты

```bash
pytest -v
```

## Структура проекта

```
app/
├── main.py          # приложение FastAPI, роутеры, сид при старте
├── config.py        # настройки из переменных окружения
├── database.py      # engine, сессии SQLAlchemy
├── models.py        # ORM-модели: User, Rider, Dragon, Quest
├── schemas.py       # Pydantic-схемы запросов/ответов
├── security.py      # пароли (PBKDF2), JWT, зависимости авторизации
├── seed.py          # демо-данные
└── routers/
    ├── auth.py      # регистрация, токен, /me
    ├── dragons.py   # CRUD драконов
    ├── riders.py    # CRUD всадников
    ├── quests.py    # CRUD квестов (+ пример X-API-Key)
    └── sandbox.py   # статус-коды, задержки, echo
```
