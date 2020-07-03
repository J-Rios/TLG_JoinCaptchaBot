# TLG_JoinCaptchaBot

Bot to verify if a new user, who joins a group, is a human.
The Bot sends an image captcha for each new user, and kicks any of them that can't solve the captcha in a specified amount of time. Also, any message that contains an URL sent by a new "user" before captcha completion will be considered Spam and will be deleted.

## Donate

Do you like this Bot? Buy me a coffee :)

Paypal:
[https://www.paypal.me/josrios](https://www.paypal.me/josrios)

BTC:
3N9wf3FunR6YNXonquBeWammaBZVzTXTyR

## Installation

Note: Use Python 3 to install and run the Bot, Python 2 support could be broken.

To generate Captchas, the Bot uses [multicolor_captcha_generator library](https://github.com/J-Rios/multicolor_captcha_generator), wich uses Pillow to generate the images.

1. Install Pillow prerequisites:

    ```bash
    apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
    ```

2. Get the project and install JoinCaptchaBot requirements:

    ```bash
    git clone --recurse-submodules https://github.com/J-Rios/TLG_JoinCaptchaBot
    pip install -r TLG_JoinCaptchaBot/requirements.txt
    ```

3. Go to project sources and give execution permission to usage scripts:

    ```bash
    cd TLG_JoinCaptchaBot/sources
    chmod +x run status kill
    ```

4. Specify Telegram Bot account Token (get it from @BotFather) in "constants.py" file:

    ```python
    'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    ```

## Usage

To ease usage a `run`, `status`, and `kill` scripts have been provided.

- Launch the Bot:  
`./run`

- Check if the script is running:  
`./status`

- Stop the Bot:  
`./kill`

## Docker

You can also run the bot on [Docker](http://docker.com). This allows easy
server migration and automates the download of all dependencies. Look at the
[docker specific documentation](docker/README.md) for more details.

## Bot Owner

The **Bot Owner** can run special commands that no one else can use, like /allowgroup (if the Bot is private, this allow groups where the Bot can be used) or /whitelist (to make Bot don't ask for captcha to some users, useful for blind users).

You can setup a Bot Owner by specifying the Telegram User ID or Alias in "constants.py" file:

```python
"BOT_OWNER": "@JoseTLG",
```

## Make Bot Private

By default, the Bot is **Public**, so any Telegram user can add and use the Bot in any group, but you can set it to be **Private** so the Bot just can be used in allowed groups (Bot owner allows them with **/allow_group** command).

You can set Bot to be Private in "constants.py" file:

```python
"BOT_PRIVATE" : True,
```

**Note:** If you have a Public Bot and set it to Private, it will leave any group where is not allowed to be used.

## Scalability (Polling or Webhook)

By default, Bot checks and receives updates from Telegram Servers by **Polling** (requests and get if there is any new updates in the Bot account corresponding to that Bot Token), this is really simple and can be used for low to median scale Bots. However, you can configure the Bot to use a **Webhook** instead if you expect to handle a large number of users/groups.

To use Webhook instead Polling, you need a signed certificate file in the system and setup the next lines in "configs.py" file to point to expected Webhook Host address, port and certificate file:

```python
"WEBHOOK_HOST": "Some IP or DNS here",
"WEBHOOK_PORT": 8443,
"WEBHOOK_CERT" : SCRIPT_PATH + "/cert.pem",
"WEBHOOK_CERT_PRIV_KEY" : SCRIPT_PATH + "/private.key",
```

To use Polling instead Webhook, just set host value back to none:

```python
"WEBHOOK_HOST": "None",
```

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

- French: [Mathieu H (Aurnytoraink)](https://github.com/Aurnytoraink)

- Italian: Noquitt

- Portuguese (Brazil): Anahuac de Paula Gil

- Catalán: Adela Casals i Jorba

- Galician: [Fernando Flores (Fer6Flores)](https://github.com/Fer6Flores); Iváns

- Basque: [xa2er](https://github.com/xa2er)

- Chinese (Mainland): [神林](https://github.com/jyxjjj)

- Indonesian: ForIndonesian

- [Unsupported, not working] Persian (Iran): [sajjad taheri](https://github.com/tgMember)

- Russian: Unattributed (anonymous)
