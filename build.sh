#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Running database migrations"
python core/manage.py makemigrations
python core/manage.py migrate --noinput

echo "==> Collecting static files"
python core/manage.py collectstatic --noinput

echo "==> Build complete"
