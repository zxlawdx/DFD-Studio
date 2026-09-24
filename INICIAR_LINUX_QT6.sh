#!/usr/bin/env bash
# Mantem o modo Qt6 isolado do ambiente virtual GTK.
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv-qt6 ]]; then
  python3 -m venv .venv-qt6
fi
source .venv-qt6/bin/activate
python -m pip install -r requirements-linux-qt6.txt
python manage.py collectstatic --no-tailwind
python launcher_linux.py
