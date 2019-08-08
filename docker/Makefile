NAME=captcha-bot
BOT_LANG ?= "EN"

ifndef BOT_TOKEN
$(error BOT_TOKEN is not set. Use make -e BOT_TOKEN=<your_bot_token>.)
endif

build:
	docker build -t "${NAME}" --build-arg BOT_TOKEN="${BOT_TOKEN}" --build-arg BOT_LANG="${BOT_LANG}" .

force:
	docker build -t "${NAME}" --no-cache --build-arg BOT_TOKEN="${BOT_TOKEN}" --build-arg BOT_LANG="${BOT_LANG}" .

.PHONY: build force
