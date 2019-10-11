# TLG_JoinCaptchaBot
Bot to verify if a new user, who join a group, is human.
The Bot send an image captcha for each new user, and kick any of them that can't solve the captcha in a specified time. Also, any message that contains an URL sent by a new "user" before captcha completion, will be considered Spam and will be deleted.

### Installation:

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

To ease usage, a run, status and kill scripts has been provided.

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

### Languages Contributors:

 - French: [Mathieu H (Aurnytoraink)](https://github.com/Aurnytoraink)

 - Italian: Noquitt

 - Portuguese (Brazil): Anahuac de Paula Gil

 - Catalán: Adela Casals i Jorba

 - Galician: [Fernando Flores (Fer6Flores)](https://github.com/Fer6Flores)

 - Basque: [xa2er](https://github.com/xa2er)

 - Chinese (Mainland): [神林](https://github.com/jyxjjj)
