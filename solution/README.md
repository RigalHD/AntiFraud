# Проект AntiFraud

## Данный ReadMe файл будет заполнен позже

## Все команды нужно выполнять, находясь в корневой папке проекта (т.е. выше папки solution/)
## Локальный запуск:

1) Установите justfile
2) Затем создайте сеть докера
- just -f solution/justfile setup_docker

### Затем выполните эти команды для первого запуска

docker run -d --name postgres \
  --network antifraud-net \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:16-alpine

docker run -d --name redis \
  --network antifraud-net \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  redis:7-alpine

docker build -f solution/Dockerfile -t antifraud .
docker run -d --name app \
  --network antifraud-net \
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

## Остановка
just -f solution/justfile stop

## Полная очистка проекта
just clear