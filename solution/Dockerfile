FROM python:3.13.11-alpine3.23

ENV APP_HOME=/home/app/
WORKDIR $APP_HOME

RUN apk add --no-cache curl

RUN mkdir ./src

RUN pip install uv
COPY ./pyproject.toml $APP_HOME
RUN uv pip install -e . --system

COPY ./src/ $APP_HOME/src/

# ENV SERVER_PORT=8080

# CMD ["sh", "-c", "exec python3 -m flask run --host=0.0.0.0 --port=$SERVER_PORT"]