#!/bin/sh
./manage.py shell -c "from load_dataset import load; load('$1')"
