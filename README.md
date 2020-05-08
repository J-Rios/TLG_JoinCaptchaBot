# TLG_JoinCaptchaBot

Bot to verify if a new user, who joins a group, is a human.
The Bot sends an image captcha for each new user, and kicks any of them that can't solve the captcha in a specified amount of time. Also, any message that contains an URL sent by a new "user" before captcha completion will be considered Spam and will be deleted.

### Installation:

Note: Use Python 3 to install and run the Bot, Python 2 support could be broken.

To generate Captchas, the Bot uses [multicolor_captcha_generator library](https://github.com/J-Rios/multicolor_captcha_generator), wich uses Pillow to generate the images.

1. Install Pillow prerequisites:
```
apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
```

2. Get the project and install JoinCaptchaBot requirements:
```
git clone --recurse-submodules https://github.com/J-Rios/TLG_JoinCaptchaBot
pip install -r TLG_JoinCaptchaBot/requirements.txt
```

3. Go to project sources and give execution permission to usage scripts:
```
cd TLG_JoinCaptchaBot/sources
chmod +x run status kill
```

4. Specify Telegram Bot account Token (get it from @BotFather) in "constants.py" file:
```
Change 'TOKEN' : 'XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

### Usage:

To ease usage a `run`, `status`, and `kill` scripts have been provided.

- Launch the Bot:
```
./run
```

- Check if the script is running:
```
./status
```

- Stop the Bot:
```
./kill
```

### Docker

You can also run the bot on [Docker](http://docker.com). This allows easy
server migration and automates the download of all dependencies. Look at the
[docker specific documentation](docker/README.md) for more details.

### Adding a New Language

Actual language support is based on external JSON files that contain all bot texts for each language.

To add support for a new language you must follow this steps:

1. Fork the project repository, clone it and create a new branch to work on it (i.e. named language-support-en).

2. Copy from one of the existing language JSON files from [here](https://github.com/J-Rios/TLG_JoinCaptchaBot/tree/master/sources/language) to a new one.

3. Change the name of that file for the language ISO Code of the language that you want.

4. Translate each text from JSON key values of the file without breaking the JSON format/structure (it should be valid for JSON parsers) and maintaining JSON key names. Keep command names in english (i.e. don't translate "START", "HELP"... /start /help ...) and don't remove special characters (like {}, ", ', \n...) too!

5. Make a pull request of that branch with the new language file into this repository and wait for it to be accepted.

6. Then, I will make the integration into source code and actual Bot account (@join_captcha_bot).

7. Enjoy the new language :)

### Languages Contributors:

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
