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
sure your bot can be invited to groups and has privacy set to _disabled_.
Without this, the bot won't be able to read messages on the group.

Save the bot token. The token _should not publicly visible_ as anyone with it
could take control of your bot instance. We'll use the token to create the
docker image containing the bot (below).

Create the docker image:

```bash
make
```

The build process may take a while, depending on your computer and connection
speeds.  Docker will indicate a successful build at the end of the process with
something like:

```bash
Successfully built (number)
Successfully tagged captcha-bot:latest
```

## Running

To run an instance, use the next command placing your Bot token to pass it as
an enviroment variable:

```bash
sudo docker run -d --name captcha-bot --env CAPTCHABOT_TOKEN="XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" captcha-bot
```

This will start the container in the background. Use `docker ps` to check if
the container is up and running, and `docker logs captcha-bot` to
investigate the logs.

You can also run with other environment variable. For list available
environment variables, please check `sources/settings.py`.

**Note on Token security**: A little bit of paranoia never hurts! Once your
container has been built, remove the lines from your bash history containing
your token. This can be accomplished with the `history -d` command on
individual lines. An easier (but coarser) approach is to run `history -c`,
followed by `history -r`. This will clear the history buffer and re-read the
history from disk.

## Stopping the bot

To stop the bot, use

```bash
docker stop captcha-bot
docker rm captcha-bot
```
