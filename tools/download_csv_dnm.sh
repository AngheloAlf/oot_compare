#! /usr/bin/env bash

set -e

# Run the script from the root of the project
DIR="$(dirname "$(readlink -f "$0")")"
cd "$DIR/.."


## Variables
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=219617635" -O - | tr -d '\r' > "dnm/tables/variables.csv"

## Functions
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/functions.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=2064898020" -O - | tr -d '\r' > "dnm/tables/code_functions.csv"
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=467726846" -O - | tr -d '\r' > "dnm/tables/boot_functions.csv"
# Mix the different functions csvs into one
cat "dnm/tables/boot_functions.csv" > "dnm/tables/functions.csv"
# TODO: include code

## boot
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=725463820"  -O - | tr -d '\r' > "dnm/tables/boot.text.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/boot.data.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/boot.rodata.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/boot.bss.csv"

## code
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=1399719350" -O - | tr -d '\r' > "dnm/tables/code.text.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/code.data.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/code.rodata.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/code.bss.csv"