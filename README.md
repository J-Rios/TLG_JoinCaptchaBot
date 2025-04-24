# TLG_JoinCaptchaBot
[![License](https://img.shields.io/github/license/J-Rios/TLG_JoinCaptchaBot)](https://github.com/J-Rios/TLG_JoinCaptchaBot/blob/master/LICENSE) [![Stars](https://img.shields.io/github/stars/J-Rios/TLG_JoinCaptchaBot)](https://github.com/J-Rios/TLG_JoinCaptchaBot/stargazers) [![Forks](https://img.shields.io/github/forks/J-Rios/TLG_JoinCaptchaBot)](https://github.com/J-Rios/TLG_JoinCaptchaBot/network/members) [![Issues](https://img.shields.io/github/issues/J-Rios/TLG_JoinCaptchaBot)](https://github.com/J-Rios/TLG_JoinCaptchaBot/issues) [![Python](https://img.shields.io/badge/python-3.6+-blue)](https://www.python.org/) [![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/join_captcha_bot) [![Maintenance](https://img.shields.io/badge/Maintained-Yes-green)](https://github.com/J-Rios/TLG_JoinCaptchaBot/graphs/commit-activity) [![GitHub last commit](https://img.shields.io/github/last-commit/J-Rios/TLG_JoinCaptchaBot)](https://github.com/J-Rios/TLG_JoinCaptchaBot/commits/master) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/J-Rios/TLG_JoinCaptchaBot/pulls)

<p align="center">
    <img width="100%" height="100%" src="https://gist.githubusercontent.com/J-Rios/05d7a8fc04166fa19f31a9608033d10b/raw/32dee32a530c0a0994736fe2d02a1747478bd0e3/captchas.png">
</p>

## Overview

TLG_JoinCaptchaBot is a Telegram Bot designed to verify that new members joining a group are humans by presenting an image-based [CAPTCHA challenge](https://en.wikipedia.org/wiki/CAPTCHA). The bot:

- Automatically sends a CAPTCHA when a new user joins
- Removes users who fail to solve the CAPTCHA within a specified time limit
- Deletes messages containing URLs sent by users who haven't completed the CAPTCHA (anti-spam)

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
  - [Systemd Service](#systemd-service)
  - [Docker](#docker)
- [Advanced Features](#advanced-features)
  - [Bot Owner Commands](#bot-owner)
  - [Private Mode](#make-bot-private)
  - [Scalability (Polling vs Webhook)](#scalability-polling-or-webhook)
- [Localization](#adding-a-new-language)
- [Languages Contributors](#languages-contributors)
- [Support Development](#donate)

## Requirements

- Python 3.6+
- Pillow and its prerequisites
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Installation

### 1. Install Pillow prerequisites

```bash
sudo apt update
sudo apt install -y make libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk
```

### 2. Install Python3 and tools

```bash
sudo apt-get install python3 python3-pip python3-venv
```

### 3. Get and setup the project

```bash
git clone https://github.com/J-Rios/TLG_JoinCaptchaBot
cd TLG_JoinCaptchaBot
make setup
```

### 4. Configure your Telegram Bot token

Edit the `src/settings.py` file:

```python
'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

## Configuration

Configuration is handled through the `src/settings.json` file. Advanced users can also use environment variables, which is useful for deployment scenarios with [virtual environments](https://docs.python.org/3/tutorial/venv.html) or [Docker](https://docs.docker.com/get-started/).

## Usage

A `Makefile` is provided for convenient operation:

```bash
# View available commands
make

# Start the bot
make start

# Check bot status
make status

# Stop the bot
make stop
```

## Deployment

### Systemd Service

To run the bot as a daemon service on systemd-based systems:

1. Create a service file:

```bash
sudo nano /etc/systemd/system/tlg_joincaptcha_bot.service
```

2. Add the following content (adjust paths as needed):

```
[Unit]
Description=Telegram Join Captcha Bot Daemon
Wants=network-online.target
After=network-online.target

[Service]
Type=forking
WorkingDirectory=/path/to/TLG_JoinCaptchaBot/src/
ExecStart=/path/to/TLG_JoinCaptchaBot/tools/start
ExecReload=/path/to/TLG_JoinCaptchaBot/tools/kill

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable --now tlg_joincaptcha_bot.service
sudo systemctl start tlg_joincaptcha_bot.service
```

4. Check service status:

```bash
sudo systemctl status tlg_joincaptcha_bot.service
```

### Docker

Docker support is available for easy deployment and server migration. See the [Docker specific documentation](docker/README.md) for details on creating a Docker container for the bot.

## Advanced Features

### Bot Owner

The bot owner can execute special commands:
- `/allowgroup`: Add groups to the allowed list (when bot is private)
- `/allowuserlist`: Exempt specific users from CAPTCHA verification (useful for accessibility needs)

Set a bot owner in `settings.py`:

```python
"BOT_OWNER": "@YourUsername",
```

### Make Bot Private

By default, anyone can add the bot to any group. To restrict usage to specific groups:

1. Set the bot to private mode in `settings.py`:

```python
"BOT_PRIVATE": True,
```

2. Use the `/allow_group` command to specify permitted groups.

**Note:** If a public group becomes a supergroup, the chat ID may change, requiring re-authorization.

### Scalability (Polling or Webhook)

#### Polling (Default)
The bot periodically checks for updates from Telegram servers. This is suitable for small to medium deployments.

#### Webhook (For larger deployments)
The bot receives updates directly from Telegram servers, which improves performance for high-traffic bots.

To configure webhook:

1. Generate SSL certificate:

```bash
openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem
```

2. Configure webhook settings in `settings.py`:

```python
"WEBHOOK_IP": "0.0.0.0",
"WEBHOOK_PORT": 8443,
"WEBHOOK_PATH": "/TLG_JoinCaptchaBot",
"WEBHOOK_CERT": SCRIPT_PATH + "/cert.pem",
"WEBHOOK_CERT_PRIV_KEY": SCRIPT_PATH + "/private.key",
```

3. For reverse proxy setups (optional):

```python
"WEBHOOK_URL": "https://example.com:8443/TLG_JoinCaptchaBot"
```

4. Enable webhook mode:

```python
"CAPTCHABOT_USE_WEBHOOK": True,
```

## Adding a New Language

The bot supports multiple languages through external JSON files. To add a new language:

1. Fork the repository and create a new branch (e.g., `language-support-xx`)
2. Copy an existing language file from the [language directory](https://github.com/J-Rios/TLG_JoinCaptchaBot/tree/master/src/language)
3. Rename the file to the ISO code of your target language
4. Translate all text values while maintaining:
   - The JSON structure and key names
   - Command names in English (`START`, `HELP`, etc.)
   - Special characters (`{}`, `"`, `'`, `\n`, etc.)
5. Submit a pull request with your translation

## Languages Contributors

- Arabic: [@damascene](https://github.com/damascene)
- Basque: [@xa2er](https://github.com/xa2er)
- Belarusian: [@antikruk](https://github.com/antikruk)
- Catalán: Adela Casals i Jorba
- Chinese (Mainland): [神林](https://github.com/jyxjjj)
- Esperanto: Pablo Busto & Porrumentzio
- Finnish: [Aminda Suomalainen (@Mikaela)](https://github.com/Mikaela)
- French: [Mathieu H (@aurnytoraink)](https://github.com/Aurnytoraink)
- Galician: [Fernando Flores (Fer6Flores)](https://github.com/Fer6Flores); Iváns
- German: [@weerdenburg](https://github.com/weerdenburg), [@MossDerg](https://github.com/MossDerg)
- Indonesian: ForIndonesian
- Italian: Noquitt, [Nicola Davide (@nidamanx)](https://github.com/nidamanx)
- Kannada: [@itsAPK](https://github.com/itsAPK)
- Korean: [@dakeshi](https://github.com/dakeshi)
- Persian: [@m4hbod](https://github.com/M4hbod)
- Portuguese (Brazil): Anahuac de Paula Gil
- Russian: Unattributed (anonymous), [@stezkoy](https://github.com/Stezkoy), [Roman (@toxi22)](https://github.com/toxi22)
- Serbo-Croatian: [@IlijaDj](https://github.com/IlijaDj)
- Slovak: [@dumontiskooo](https://t.me/dumontiskooo)
- Ukrainian: Vadym Zhushman (@zhushman00), [Roman (@toxi22)](https://github.com/toxi22)
- Uzbek: [@mhwebuz](https://github.com/mhwebuz)

## Donate

If you find this bot useful, consider supporting the developer:

Paypal: [https://www.paypal.me/josrios](https://www.paypal.me/josrios)
