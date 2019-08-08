FROM debian:buster

MAINTAINER Marco Paganini <paganini@paganini.net>

ARG BOT_PROJECT="captcha-bot"
ARG BOT_USER="captcha-bot"
ARG BOT_HOME_DIR="/home/${BOT_USER}"
ARG GITHUB_URL="https://github.com/J-Rios/TLG_JoinCaptchaBot"

# Change this to an user_id that does not own anything on the host.
ARG UID=62999

# This represents an invalid token and should always exist in
# the "stock" constants.py file.
ARG INVALID_TOKEN="XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Use the BOT_TOKEN argument to override your token.  We don't use environment
# here, since there's no need to have the token available to the container as
# an environment variable.
ARG BOT_TOKEN

# Default language (override when building -- must be all CAPS.)
ARG BOT_LANG="EN"

# OS and base environment layer.
RUN groupadd --gid ${UID} ${BOT_USER} && \
    useradd --uid ${UID} --gid ${UID} --shell /bin/bash --home-dir ${BOT_HOME_DIR} ${BOT_USER} && \
    apt-get update && \
    apt-get install --yes bash coreutils git procps python3 python3-pip && \
    apt-get install --yes libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

# TLG captcha bot layer.
RUN mkdir -p "${BOT_HOME_DIR}" && \
    cd "${BOT_HOME_DIR}" && \
    git clone --recurse-submodules "${GITHUB_URL}" && \
    # In Debian, installing the telegram library in the requirements.txt file
    # causes imports to fail.
    pip3 install python_telegram_bot==11.1.0 && \
    pip3 install Pillow==6.0.0 && \
    cd TLG_JoinCaptchaBot/sources && \
    sed -i -e "s/${INVALID_TOKEN}/${BOT_TOKEN}/g" constants.py && \
    sed -i -e "s/^\(\s\+'INIT_LANG'\)[^:]*:.*/\1 : '${BOT_LANG}',/g" constants.py && \
    chown -R "${BOT_USER}":"${BOT_USER}" "${BOT_HOME_DIR}" && \
    echo "rm -f ./data/captchas/*; python3 -u join_captcha_bot.py" >run_in_docker && \
    chmod 755 kill run run_in_docker status && \
    cd ..


CMD ["/bin/su", "-", "captcha-bot", "-c", "bash -c 'cd /home/captcha-bot/TLG_JoinCaptchaBot/sources && ./run_in_docker'"]
