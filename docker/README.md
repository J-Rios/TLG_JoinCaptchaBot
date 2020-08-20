# Docker configuration

This document lists the requirements and steps to run
[TLG_JoinCaptchaBot](https://github.com/J-Rios/TLG_JoinCaptchaBot) in a docker
container.

## Pre-requisites

* [docker](https://www.docker.com/products/docker-engine). If possible, install
  it using your OS native packaging system (under Debian based systems, use
  `apt-get install docker-ce`).

* GNU Make, which should be installed on most Linux distributions by default.

## Building a new image

Create a new bot on Telegram using [The BotFather](http://t.me/BotFather). Make
sure your bot can be invited to channels and has privacy set to _disabled_.
Without this, the bot won't be able to read messages on the channel.

Save the bot token. The token _should not publicly visible_ as anyone with it
could take control of your bot instance.  We'll use the token to create the
docker image containing the bot (below).

Create a docker image:

```bash
make BOT_TOKEN="<your_bot_token_here>"
```

It is also possible to specify a different default language for the bot to use
by setting the `BOT_LANG` variable at build time, like:

```bash
make BOT_TOKEN="<your_bot_token_here>" BOT_LANG="PT_BR"
```

The build process may take a while, depending on your computer and connection
speeds.  Docker will indicate a successful build at the end of the process with
something like:

```bash
Successfully built (number)
Successfully tagged captcha-bot:latest
```

**Note on token security**: A little bit of paranoia never hurts! Once your
container has been built, remove the lines from your bash history containing
your token. This can be accomplished with the `history -d` command on
individual lines. An easier (but coarser) approach is to run `history -c`,
followed by `history -r`. This will clear the history buffer and re-read the
history from disk.

## Running

To run an instance, use:

```bash
docker run -d --name captcha-bot captcha-bot
```

This will start the container in the background. Use `docker ps` to check if
the container is up and running, and `docker logs captcha-bot` to
investigate the logs.

## Stopping the bot

To stop the bot, use

```bash
docker stop captcha-bot
docker rm captcha-bot
```
