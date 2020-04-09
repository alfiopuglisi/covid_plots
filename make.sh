#!/bin/sh

cd ../COVID-19-italia
git pull
A="`git log -1 --format="%at" | xargs -I{}  date -d @{} "+%Y-%m-%d %H:%M:%S" --utc` UTC"

cd ../COVID-19-world
git pull
B="`git log -1 --format="%at" | xargs -I{}  date -d @{} "+%Y-%m-%d %H:%M:%S" --utc` UTC"

cd ../covid_plots
/home/public/puglisi/anaconda3/bin/python italia.py "$A"
/home/public/puglisi/anaconda3/bin/python us.py "$B"
/home/public/puglisi/anaconda3/bin/python row.py "$B"

