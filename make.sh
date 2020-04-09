#!/bin/sh

cd ../COVID-19-italia
git pull
A="`git log -1 --format="%at" | xargs -I{}  date -d @{} "+%Y-%m-%d %H:%M:%S" --utc` UTC"

cd ../COVID-19-world
git pull
B="`git log -1 --format="%at" | xargs -I{}  date -d @{} "+%Y-%m-%d %H:%M:%S" --utc` UTC"

cd ../covid_plots
python italia.py "$A"
python us.py "$B"
python row.py "$B"

