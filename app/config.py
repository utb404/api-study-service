"""Настройки приложения.

Значения можно переопределить через переменные окружения —
удобно при запуске в Docker или на хостинге.
"""
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dragon-academy-super-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./academy.db")

# Демонстрационный API-ключ для эндпоинтов, защищённых заголовком X-API-Key
API_KEY = os.getenv("API_KEY", "sky-fire-9000")
