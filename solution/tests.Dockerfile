FROM python:3.13.11-slim

ENV APP_HOME=/home/app/
WORKDIR $APP_HOME

RUN mkdir ./src

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install uv

COPY ./pyproject.toml $APP_HOME
COPY ./src/ $APP_HOME/src/
COPY ./tests/ $APP_HOME/tests/

RUN uv pip install -e ".[test]" --system

CMD ["sh", "-c", "exec backend run api"]