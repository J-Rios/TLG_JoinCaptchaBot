#!/usr/bin/env bash

# Actual script directory path
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Clean old/previous residual captcha images
rm -f $DIR/../src/data/captchas/*

# Launch the Bot
exec python3 -u $DIR/../src/oin_captcha_bot_pro.py
