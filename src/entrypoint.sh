#!/usr/bin/env bash

# Actual script directory path
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

rm -f $DIR/data/captchas/*

exec python3 -u $DIR/join_captcha_bot.py
