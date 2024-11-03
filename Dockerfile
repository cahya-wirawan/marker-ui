FROM python:3.12.7-slim-bullseye

ARG UID=11132
ARG GID=11133
ENV HOME=/home/llm-apps
RUN addgroup --gid $GID llm-adm && adduser --uid $UID --ingroup llm-adm --disabled-password -q --gecos llm llm-apps

ARG APP_DIR=/app
WORKDIR $APP_DIR
COPY src assets data ./
COPY requirements.txt run.sh ./
RUN chown -R $UID:$GID $APP_DIR

USER $UID:$GID
RUN python -m venv $APP_DIR/.venv && . $APP_DIR/.venv/bin/activate && pip install -r requirements.txt

ENTRYPOINT ["/bin/sh", "-c", "/app/run.sh"]
