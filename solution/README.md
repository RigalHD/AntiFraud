# Проект AntiFraud

## В данной ветке будет находиться доработанная версия проекта с фиксами нескольких важных багов и недочетов

Проект писался с использованием Чистой Архитектуры
Реализованный уровень DSL - 3
Batch транзакции не поддерживаются
Статистика не поддерживается

# Локальный запуск (из директории solution/)
### Проект
(Требуется установленный на пк justfile (Или же rust-just через pip))
```
just run
```
### Тесты
```
just tests
```
### Миграции
```
just migration Migration changes text
```
### Остановка
```
just down
```
### Очистка 
```
just clear
```
### Запуск линтеров
```
uv pip install -e ".[lint]"
just lint
```

# Локальный запуск БЕЗ docker-compose. Запускается тот же Dockerfile, который запускает gitlab ci
 Все команды нужно выполнять, находясь в корневой папке проекта (т.е. выше папки solution/)

1) Установите justfile
2) Затем создайте сеть докера
docker network create antifraud-net

### Затем выполните эти команды для первого запуска
```
docker run -d --name postgres \
  --network antifraud-net \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:16-alpine

docker build -f solution/Dockerfile -t antifraud .
docker run -d --name app \
  --network antifraud-net \
  -v $(pwd)/solution/src/backend/infrastructure/database/alembic/migrations/versions:/home/app/src/backend/infrastructure/database/alembic/migrations/versions \
  -e ADMIN_EMAIL=admin@mail.ru \
  -e ADMIN_FULLNAME=Test\ Test \
  -e ADMIN_PASSWORD=123123123aA! \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=testdb \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e RANDOM_SECRET=Jf/ZpZSxfMWnOexP48Mp1z200jd+8BVZ7ws6Uw5Jp/w= \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  -p 8080:8080 \
  antifraud
```


## Тесты:
### Создайте сеть для тестов:
docker network create antifraud-test-net

### Запустите контейнеры: 
docker run -d --name postgres-test \
  --network antifraud-test-net \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=testdb_test \
  postgres:16-alpine

docker build -f solution/tests.Dockerfile -t antifraud-tests .
docker run --rm \
  --name antifraud-tests-app \
  --network antifraud-test-net \
  -e ADMIN_EMAIL=admin@mail.ru \
  -e ADMIN_FULLNAME=Test\ Test \
  -e ADMIN_PASSWORD=123123123aA! \
  -e DB_HOST=postgres-test \
  -e DB_PORT=5432 \
  -e DB_NAME=testdb_test \
  -e RANDOM_SECRET=Jf/ZpZSxfMWnOexP48Mp1z200jd+8BVZ7ws6Uw5Jp/w= \
  -e DB_USER=testuser \
  -e DB_PASSWORD=testpass \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  antifraud-tests

docker run --rm \
  --network antifraud-test-net \
  -e ADMIN_EMAIL=admin@mail.ru \
  -e ADMIN_FULLNAME=Test\ Test \
  -e ADMIN_PASSWORD=123123123aA! \
  -e DB_HOST=postgres-test \
  -e DB_PORT=5432 \
  -e DB_NAME=testdb_test \
  -e RANDOM_SECRET=Jf/ZpZSxfMWnOexP48Mp1z200jd+8BVZ7ws6Uw5Jp/w= \
  -e DB_USER=testuser \
  -e DB_PASSWORD=testpass \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  -e API_URL=http://antifraud-tests-app:8080/api/v1/ \
  antifraud-tests \
  pytest -vvv

## Удаление контейнеров с тестами
docker rm -f postgres-test redis-test antifraud-tests-app