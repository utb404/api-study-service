"""Утилитные эндпоинты в духе httpbin — для отладки клиентов и тренировок."""
import asyncio
import random

from fastapi import APIRouter, Query, Request, Response, status
from pydantic import BaseModel

router = APIRouter(prefix="/sandbox", tags=["Песочница"])


class EchoResponse(BaseModel):
    method: str
    url: str
    headers: dict[str, str]
    query_params: dict[str, str]
    body: str


@router.get(
    "/status/{code}",
    summary="Вернуть произвольный HTTP-статус",
    description="Например, `/sandbox/status/418` вернёт 418 I'm a teapot.",
)
def status_code(code: int):
    if not 100 <= code <= 599:
        return Response(
            content='{"detail": "Код должен быть в диапазоне 100–599"}',
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/json",
        )
    return Response(
        content=f'{{"status": {code}}}',
        status_code=code,
        media_type="application/json",
    )


@router.get(
    "/delay/{seconds}",
    summary="Ответ с задержкой (тест таймаутов)",
    description="Максимум 10 секунд.",
)
async def delay(seconds: float):
    seconds = max(0.0, min(seconds, 10.0))
    await asyncio.sleep(seconds)
    return {"slept_seconds": seconds}


@router.api_route(
    "/echo",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    response_model=EchoResponse,
    summary="Эхо: вернуть детали запроса",
    description="Принимает любой из методов GET/POST/PUT/PATCH/DELETE "
    "и возвращает метод, заголовки, query-параметры и тело.",
)
async def echo(request: Request):
    body = await request.body()
    return EchoResponse(
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        body=body.decode("utf-8", errors="replace"),
    )


@router.get("/headers", summary="Вернуть заголовки запроса")
async def headers(request: Request):
    return {"headers": dict(request.headers)}


@router.get(
    "/random-dragon-name",
    summary="Случайное драконье имя",
    description="Бесполезно, но весело. Поддерживает параметр `count`.",
)
def random_dragon_name(count: int = Query(1, ge=1, le=20)):
    prefixes = ["Гром", "Пепел", "Ледо", "Тене", "Огне", "Вихре", "Звездо", "Мгло"]
    suffixes = ["клык", "крыл", "хвост", "коготь", "глаз", "рог", "шип", "вей"]
    names = [random.choice(prefixes) + random.choice(suffixes) for _ in range(count)]
    return {"names": names}
