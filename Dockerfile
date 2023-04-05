FROM python:3.10.9-bullseye
EXPOSE 7001


ENV PYTHONUNBUFFERED 1
ENV PIP_CONFIG_FILE pip.conf

ENV APP_USER service_user
ENV C_FORCE_ROOT true


COPY pip.conf .
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    && rm -rf /root/.cache
COPY . .
