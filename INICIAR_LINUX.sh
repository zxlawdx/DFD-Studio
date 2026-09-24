#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then python3 -m venv .venv --system-site-packages; fi
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py collectstatic --no-tailwind
python manage.py runapp
