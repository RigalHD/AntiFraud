# Local run

Full requirements and environment variables are in `./assignment.md` and `../openapi.yml`.

## Docker image requirements

The Docker image must include the `curl` utility — autotests use it for health checks. Project templates already have `curl` installed. If you change the base image or Dockerfile, make sure `curl` is present.

## Quick check, what's "alive"

1) Start the dependencies (minimum PostgreSQL):

```bash
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:16-alpine
```

2) Build and run the application (for example, the path to the Dockerfile depends on the starter template, often `solution/`):

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

3) Check that the server responds:

```bash
curl http://localhost:8080/api/v1/ping
```
