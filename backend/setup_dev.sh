#!/bin/bash
set -e

python3 manage.py migrate
python3 manage.py seed_admin
python3 manage.py seed_menu