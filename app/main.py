from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.database import Base, SessionLocal, engine
from app.routers import auth, dragons, quests, riders, sandbox
from app.seed import seed

DESCRIPTION = """
**Dragon Academy API** — учебный сервис-песочница для тренировки работы с REST API
(по мотивам futuramaapi, но во вселенной Академии драконьих всадников 🐉).

Что здесь можно потренировать:

* **GET** — списки с пагинацией (`limit`/`offset`), фильтры и поиск;
* **POST / PUT / PATCH / DELETE** — полный CRUD над драконами, всадниками и квестами;
* **Авторизацию JWT (Bearer)** — регистрация, получение токена, защищённые эндпоинты;
* **Авторизацию по API-ключу** — заголовок `X-API-Key` (удаление квестов);
* **Отладку клиента** — `/sandbox/*`: произвольные статус-коды, задержки, echo.

Демо-доступы:

* пользователь **demo / demo1234** (для `/auth/token`);
* API-ключ **sky-fire-9000** (заголовок `X-API-Key`).

Чтение (GET) открыто без авторизации. База пересоздаётся при удалении файла `academy.db`.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(
    title="Dragon Academy API",
    description=DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    contact={"name": "Академия драконьих всадников"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dragons.router)
app.include_router(riders.router)
app.include_router(quests.router)
app.include_router(sandbox.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Служебное"], summary="Проверка живости сервиса")
def health():
    return {"status": "ok", "service": "dragon-academy-api"}
