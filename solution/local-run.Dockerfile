FROM python:3.13.11-alpine3.23

ENV APP_HOME=/home/app/
WORKDIR $APP_HOME

RUN apk add --no-cache curl

RUN mkdir ./src

RUN pip install uv

COPY ./pyproject.toml $APP_HOME
COPY ./src/ $APP_HOME/src/
RUN uv pip install -e . --system