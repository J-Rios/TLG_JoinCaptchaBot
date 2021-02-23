
SHELL = /bin/bash
NAME = captcha-bot
DOCKERFILE = Dockerfile


.PHONY: build force test debug

build:
	docker build -f "${DOCKERFILE}" -t "${NAME}" .

force:
	docker build -f "${DOCKERFILE}" -t "${NAME}" --no-cache .

test:
	$(MAKE)
	docker run -it $(NAME):latest

debug:	test
	docker run -it --user=root --entrypoint ${SHELL} $(NAME):latest
