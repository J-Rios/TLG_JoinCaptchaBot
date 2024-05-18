# TLG_JoinCaptchaBot

<p align="center">
    <img width="100%" height="100%" src="https://gist.githubusercontent.com/J-Rios/05d7a8fc04166fa19f31a9608033d10b/raw/32dee32a530c0a0994736fe2d02a1747478bd0e3/captchas.png">
</p>

Bot to verify if a new user, who joins a group, is a human.
The Bot sends an image captcha for each new user, and kicks any of them that can't solve the captcha in a specified amount of time. Also, any message that contains an URL sent by a new "user" before captcha completion will be considered Spam and will be deleted.

## Donate

Do you like this Bot? Buy me a coffee :)

Paypal:

[https://www.paypal.me/josrios](https://www.paypal.me/josrios)

## Installation

Note: Use Python 3.6 or above to install and run the Bot, previous version are unsupported.

To generate Captchas, the Bot uses [multicolor_captcha_generator library](https://github.com/J-Rios/multicolor_captcha_generator), which uses Pillow to generate the images.

1. Install Pillow prerequisites:

    ```bash
    sudo apt install -y libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
    ```

2. Get the project and install JoinCaptchaBot requirements:

    ```bash
    git clone https://github.com/J-Rios/TLG_JoinCaptchaBot
    python3 -m pip install -r TLG_JoinCaptchaBot/requirements.txt
    ```

3. Go to project sources and give execution permission to usage scripts:

    ```bash
    cd TLG_JoinCaptchaBot/sources
    chmod +x run status kill
    ```

4. Specify Telegram Bot account Token (get it from @BotFather) in "settings.py" file:

    ```python
    'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    ```

## Usage

To ease usage a `run`, `status`, and `kill` scripts have been provided.

- Launch the Bot:

    ```bash
    ./run
    ```

- Check if the script is running:

    ```bash
    ./status
    ```

- Stop the Bot:

    ```bash
    ./kill
    ```

## Systemd service

For systemd based systems, you can setup the Bot as daemon service.

To do that, you need to create a new service description file for the Bot as follow:

```bash
[vim or nano] /etc/systemd/system/bot.service
```

File content:

```bash
[Unit]
Description=Bot Telegram Daemon
Wants=network-online.target
After=network-online.target

[Service]
Type=forking
WorkingDirectory=/path/to/dir/sources/
ExecStart=/path/to/dir/sources/run
ExecReload=/path/to/dir/sources/kill

[Install]
WantedBy=multi-user.target
```

Then, to add the new service into systemd, you should enable it:

```bash
systemctl enable --now bot.service
```

Remember that, if you wan't to disable it, you should execute:

```bash
systemctl disable bot.service
```

## Docker

You can also run the bot on [Docker](https://docs.docker.com/get-started/). This allows easy
server migration and automates the download of all dependencies. Look at the
[docker specific documentation](docker/README.md) for more details about how to create a Docker Container for Captcha Bot.

## Bot Owner

The **Bot Owner** can run special commands that no one else can use, like /allowgroup (if the Bot is private, this allow groups where the Bot can be used) or /allowuserlist (to make Bot don't ask for captcha to some users, useful for blind users).

You can setup a Bot Owner by specifying the Telegram User ID or Alias in "settings.py" file:

```python
"BOT_OWNER": "@JoseTLG",
```

## Make Bot Private

By default, the Bot is **Public**, so any Telegram user can add and use the Bot in any group, but you can set it to be **Private** so the Bot just can be used in allowed groups (Bot owner allows them with **/allow_group** command).

You can set Bot to be Private in "settings.py" file:

```python
"BOT_PRIVATE" : True,
```

**Note:** If you have a Public Bot and set it to Private, it will leave any group where is not allowed to be used when a new user joins.

**Note:** Telegram Private Groups could changes their chat ID when it become a public super-group, so the Bot will leave the group and the owner has to set the new group chat ID with /allow_group.

## Scalability (Polling or Webhook)

By default, Bot checks and receives updates from Telegram Servers by **Polling** (it periodically requests and gets from Telegram Server if there is any new updates in the Bot account corresponding to that Bot Token), this is really simple and can be used for low to median scale Bots. However, you can configure the Bot to use **Webhook** instead if you expect to handle a large number of users/groups (with webhook, the Telegram Server is the one that will connect to you machine and send updates to the Bot when there is any new update).

To use Webhook instead Polling, you need a signed certificate file in the system, you can create the key file and self-sign the cert through openssl tool:

```bash
openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem
```

Once you have the key and cert files, setup the next lines in "settings.py" file to point to expected host system address, port, path and certificate files:

```python
"WEBHOOK_IP": "0.0.0.0",
"WEBHOOK_PORT": 8443,
"WEBHOOK_PATH": "/TLG_JoinCaptchaBot"
"WEBHOOK_CERT" : SCRIPT_PATH + "/cert.pem",
"WEBHOOK_CERT_PRIV_KEY" : SCRIPT_PATH + "/private.key",
```

(Optional) In case you want to use a reverse proxy between Telegram Server and the system that runs the Bot, you need to setup the Proxy Webhook URL setting:

```python
"WEBHOOK_URL": "https://example.com:8443/TLG_JoinCaptchaBot"
```

Then, you need to change Bot connection mode from polling to webhook by setting to True the next configuration:

```python
"CAPTCHABOT_USE_WEBHOOK": True,
```

To go back and use Polling instead Webhook, just set the config back to False:

```python
"CAPTCHABOT_USE_WEBHOOK": False,
```

## Environment Variables Setup

You can setup some Bot properties manually changing their values in settings.py file, but also you can use environment variables to setup all that properties (this is really useful for advance deployment when using [Virtual Environments](https://docs.python.org/3/tutorial/venv.html) and/or [Docker](https://docs.docker.com/get-started/) to isolate the Bot process execution).

## Adding a New Language

Actual language support is based on external JSON files that contain all bot texts for each language.

To add support for a new language you must follow this steps:

1. Fork the project repository, clone it and create a new branch to work on it (i.e. named language-support-en).

2. Copy from one of the existing language JSON files from [here](https://github.com/J-Rios/TLG_JoinCaptchaBot/tree/master/sources/language) to a new one.

3. Change the name of that file for the language ISO Code of the language that you want.

4. Translate each text from JSON key values of the file without breaking the JSON format/structure (it should be valid for JSON parsers) and maintaining JSON key names. Keep command names in english (i.e. don't translate "START", "HELP"... /start /help ...) and don't remove special characters (like {}, ", ', \n...) too!

5. Make a pull request of that branch with the new language file into this repository and wait for it to be accepted.

6. Then, I will make the integration into source code and actual Bot account (@join_captcha_bot).

7. Enjoy the new language :)

## Languages Contributors

- Arabic: [@damascene](https://github.com/damascene)

- Basque: [@xa2er](https://github.com/xa2er)

- Belarusian: [@antikruk](https://github.com/antikruk)

- Catalán: Adela Casals i Jorba

- Chinese (Mainland): [神林](https://github.com/jyxjjj)

- Esperanto: Pablo Busto & Porrumentzio.

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

- Slovak: [@dumontiskooo](https://t.me/dumontiskooo)

- Ukrainian: Vadym Zhushman (@zhushman00), [Roman (@toxi22)](https://github.com/toxi22)

- Uzbek: [@mhwebuz](https://github.com/mhwebuz)
