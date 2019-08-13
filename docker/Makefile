NAME = captcha-bot
BOT_LANG ?= EN
SUPPORTED_LANGUAGES = EN ES CA GL PT_BR ZH_CN

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

build:
	docker build -t "${NAME_LOW}" --build-arg BOT_TOKEN="${BOT_TOKEN}" --build-arg BOT_LANG="${BOT_LANG_UPP}" .

force:
	docker build -t "${NAME_LOW}" --no-cache --build-arg BOT_TOKEN="${BOT_TOKEN}" --build-arg BOT_LANG="${BOT_LANG_UPP}" .

.PHONY: build force
