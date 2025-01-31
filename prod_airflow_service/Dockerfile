FROM apache/airflow:latest

USER root

RUN apt-get update \
    && apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libx11-xcb1 \
    libgbm1 \
    libasound2 \
    libxss1 \
    libnss3 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && apt-get install -y libvulkan1 \
    && curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get install -f -y \
    && rm google-chrome-stable_current_amd64.deb

WORKDIR /opt/airflow

USER airflow

RUN pip install --no-cache-dir apache-airflow-providers-docker \
    apache-airflow-providers-google \
    psycopg2-binary \
    pyyaml \
    google-cloud-bigquery \
    google-auth \
    pandas \
    requests \
    pytz \
    google-api-core \
    selenium