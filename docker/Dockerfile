# This Dockerfile has buildkit syntax, to allow build steps to be cached
# and speed up when rebuilding

FROM python:3.8.8-slim-buster AS base

# Build ARGs
ARG BOT_PROJECT="captcha-bot"
ARG BOT_USER="nobody"
ARG BOT_GROUP="nogroup"
ARG BOT_HOME_DIR="/srv"
ARG APP_DIR="${BOT_HOME_DIR}/app"
ARG GITHUB_URL="https://github.com/J-Rios/TLG_JoinCaptchaBot"

# Export ARGs as ENV vars so they can be shared among steps
ENV BOT_PROJECT="${BOT_PROJECT}" \
    BOT_USER="${BOT_USER}" \
    BOT_GROUP="${BOT_GROUP}" \
    BOT_HOME_DIR="${BOT_HOME_DIR}" \
    APP_DIR="${APP_DIR}" \
    GITHUB_URL="${GITHUB_URL}" \
    DEBIAN_FRONTEND=noninteractive \
    APT_OPTS="-q=2 --no-install-recommends --yes"

# Prepare a directory to run with an unprivileged user
RUN chown -cR "${BOT_USER}:${BOT_GROUP}" ${BOT_HOME_DIR} && \
    usermod -d ${BOT_HOME_DIR} ${BOT_USER}

################################################################################

FROM base AS builder-deps

# Install build dependencies
RUN apt-get ${APT_OPTS} update && \
    apt-get ${APT_OPTS} install \
    build-essential \
    git \
    procps  \
    libtiff5-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk

################################################################################

FROM builder-deps AS builder

# Build the code as unprivileged user
USER ${BOT_USER}
WORKDIR ${BOT_HOME_DIR}
RUN git clone ${GITHUB_URL} ${APP_DIR} && \
    python3 -m pip install --user --requirement ${APP_DIR}/requirements.txt && \
    cd ${APP_DIR}/src && \
    chown -cR ${BOT_USER}:${BOT_GROUP} ${BOT_HOME_DIR} && \
    rm -rf ${BOT_HOME_DIR}/.cache && \
    find ${APP_DIR} -iname '.git*' -print0 | xargs -0 -r -t rm -rf

################################################################################

FROM base AS app

# Address the pip warning regarding PATH
ENV PATH="${PATH}:${BOT_HOME_DIR}/.local/bin"

# Import built code from previous step
COPY --from=builder ${BOT_HOME_DIR} ${BOT_HOME_DIR}

# Adjust privileges
RUN chown -R "${BOT_USER}:${BOT_GROUP}" ${BOT_HOME_DIR} && \
    usermod -d ${BOT_HOME_DIR} ${BOT_USER}

# Set up to run as an unprivileged user
USER ${BOT_USER}
WORKDIR ${APP_DIR}/src
CMD ["./entrypoint.sh"]
