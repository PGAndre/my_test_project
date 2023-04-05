FROM python:3.10.9-slim-bullseye

EXPOSE 7001

ENV PYTHONUNBUFFERED 1
ENV PIP_CONFIG_FILE pip.conf
ENV C_FORCE_ROOT true

COPY pip.conf requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt && \
    rm -rf /root/.cache

COPY . .