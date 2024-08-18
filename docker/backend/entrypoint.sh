#!/bin/sh
cd /src
/callback.py
if [ $? -ne 0 ]; then
  exit 255
else 
  if [ "${ENV_TYPE}" = "dev" ]; then
    exec python -m uvicorn backend.main:app --reload --host 0.0.0.0
  else
    exec python -m gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 backend.main:app
  fi
fi



