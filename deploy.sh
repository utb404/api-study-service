#!/usr/bin/env bash
# Деплой Dragon Academy API на сервер с Ubuntu/Debian.
#
#   ./deploy.sh                          — HTTP по IP сервера (порт 80)
#   DOMAIN=api.example.com ./deploy.sh   — HTTPS с автосертификатом Let's Encrypt
#
# Скрипт ставит Docker (если его нет), генерирует SECRET_KEY в .env
# и поднимает приложение через docker compose. Повторный запуск
# обновляет сервис (git pull делайте сами перед запуском).
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
    echo "==> Docker не найден, устанавливаю (потребуются права root)..."
    curl -fsSL https://get.docker.com | sh
fi

if [ ! -f .env ]; then
    echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
    echo "==> Создан .env со случайным SECRET_KEY"
fi

if [ -n "${DOMAIN:-}" ]; then
    if grep -q '^DOMAIN=' .env; then
        sed -i "s|^DOMAIN=.*|DOMAIN=${DOMAIN}|" .env
    else
        echo "DOMAIN=${DOMAIN}" >> .env
    fi
    echo "==> Домен: ${DOMAIN} (HTTPS включится автоматически)"
fi

echo "==> Собираю и запускаю контейнеры..."
docker compose up -d --build

echo
echo "==> Готово!"
if [ -n "${DOMAIN:-}" ]; then
    echo "    Документация API: https://${DOMAIN}/docs"
    echo "    (убедитесь, что DNS-запись домена указывает на этот сервер)"
else
    IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "IP-сервера")
    echo "    Документация API: http://${IP}/docs"
fi
echo "    Логи:      docker compose logs -f"
echo "    Остановка: docker compose down"
