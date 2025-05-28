ARG PYTHON_VERSION=3.9.9
FROM python:${PYTHON_VERSION}-alpine3.15

ARG ENVIRONMENT
ENV APP_ENV=${ENVIRONMENT:-test}

WORKDIR /app

COPY requirements.txt .

# Instalamos dependencias necesarias para compilar pandas y otras librerías
RUN apk update && \
    apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    g++ \
    libffi-dev \
    cairo-dev \
    pango-dev \
    gdk-pixbuf-dev \
    libxml2-dev \
    glib-dev \
    cairo \
    pango \
    gdk-pixbuf \
    fontconfig \
    ttf-freefont \
    chrony \
    openblas-dev \
    gfortran \
    tzdata && \
    fc-cache -fv && \
    cp /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    echo "Asia/Kolkata" > /etc/timezone && \
    pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt && \
    rm -rf /var/cache/apk/*

RUN mkdir -p /var/log/application/
ENV PYTHONPATH /app

EXPOSE 7093

COPY . .

CMD ["sh", "-c", "chronyd -f /etc/chrony/chrony.conf -d -x & uvicorn app.main:app --host 0.0.0.0 --port 7093"]