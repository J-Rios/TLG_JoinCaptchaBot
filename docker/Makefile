SHELL = /bin/bash
NAME = captcha-bot
BOT_LANG ?= EN
SUPPORTED_LANGUAGES = AR CA DE EN EO ES EU FR GL ID IT NL PL PT_BR RU TR ZH_CN
DOCKERFILE = Dockerfile

# Check if Bot token has been provided
ifndef BOT_TOKEN
    $(error BOT_TOKEN is not set. Use make -e BOT_TOKEN=<your_bot_token>.)
endif

# Set docker container build name to lowercases
NAME_LOW = $(shell echo $(NAME) | tr A-Z a-z)

# Set bot language argument to uppercases
BOT_LANG_UPP = $(shell echo $(BOT_LANG) | tr a-z A-Z)

# Check if it is a supported language argument
VALID_LANG = $(foreach lang, $(SUPPORTED_LANGUAGES),$(if $(findstring $(lang), $(BOT_LANG_UPP)),true))
ifneq ($(strip $(VALID_LANG)), true)
    $(info  )
    $(info Provided default language: $(BOT_LANG_UPP))
    $(info Languages supported: $(SUPPORTED_LANGUAGES))
    $(error Invalid default language provided)
endif

.PHONY: build force test debug

build:
	docker build -f "${DOCKERFILE}" -t "${NAME_LOW}" --build-arg BOT_TOKEN="${BOT_TOKEN}" --build-arg BOT_LANG="${BOT_LANG_UPP}" .

force:
	docker build -f "${DOCKERFILE}" -t "${NAME_LOW}" --no-cache --build-arg BOT_TOKEN="${BOT_TOKEN}" --build-arg BOT_LANG="${BOT_LANG_UPP}" .

test:
	$(MAKE) -e BOT_TOKEN=XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	docker run -it $(NAME_LOW):latest

debug:	test
	docker run -it --user=root --entrypoint ${SHELL} $(NAME_LOW):latest
