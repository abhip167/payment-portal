#!/usr/bin/env bash

# Set defaults if not provided in environment
: "${MODULE_NAME:=app.main}"
: "${VARIABLE_NAME:=app}"
: "${APP_MODULE:=$MODULE_NAME:$VARIABLE_NAME}"
: "${HOST:=0.0.0.0}"
: "${PORT:=8000}"
: "${LOG_LEVEL:=info}"

# Start uvicorn with live-reload
uvicorn \
    --reload \
    --proxy-headers \
    --host "$HOST" \
    --port "$PORT" \
    "$APP_MODULE"