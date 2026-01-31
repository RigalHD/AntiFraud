# Локальный запуск

Полные требования и переменные окружения — в `./assignment.md` и `../openapi.yml`.

## Требования к Docker-образу

Docker-образ должен содержать утилиту `curl` — автопроверка использует её для health-check. В шаблонах `curl` уже установлен. Если меняете базовый образ или Dockerfile, убедитесь, что `curl` присутствует.

## Быстрая проверка, что «живет».

1) Поднимите зависимости (минимум PostgreSQL):

```bash
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:16-alpine
```

2) Соберите и запустите приложение (пример; путь к Dockerfile зависит от стартового шаблона, часто это `solution/`):

```bash
docker build -f solution/Dockerfile -t antifraud .
docker run -d --name app \
  -e ADMIN_EMAIL=admin@mail.ru \
  -e ADMIN_FULLNAME="Test Test" \
  -e ADMIN_PASSWORD="123123123aA!" \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=testdb \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e RANDOM_SECRET=Jf/ZpZSxfMWnOexP48Mp1z200jd+8BVZ7ws6Uw5Jp/w= \
  -p 8080:8080 \
  antifraud
```

3) Проверьте, что сервер отвечает:

```bash
curl http://localhost:8080/api/v1/ping
```
