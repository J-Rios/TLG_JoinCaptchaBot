# This Dockerfile has buildkit syntax, to allow build steps to be cached
# and speed up when rebuilding

# TODO: Check if we can build this FROM python:3-alpine to slim down the image

FROM python:3-slim-buster AS base

# Build ARGs
ARG BOT_PROJECT="captcha-bot"
ARG BOT_USER="nobody"
ARG BOT_GROUP="nogroup"
ARG BOT_HOME_DIR="/srv"
ARG REPO_NAME="TLG_JoinCaptchaBot"
ARG GITHUB_URL="https://github.com/LIDSoL/${REPO_NAME}"

# This represents an invalid token and should always exist in
# the "stock" constants.py file.
ARG INVALID_TOKEN="XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Use the BOT_TOKEN argument to override your token.  We don't use environment
# here, since there's no need to have the token available to the container as
# an environment variable.
ARG BOT_TOKEN

# Default language (override when building -- must be all CAPS.)
# check Makefile for a list of supported languages
ARG BOT_LANG="EN"

# Export ARGs as ENV vars so they can be shared among steps
ENV BOT_PROJECT="${BOT_PROJECT}" \
    BOT_USER="${BOT_USER}" \
    BOT_GROUP="${BOT_GROUP}" \
    BOT_HOME_DIR="${BOT_HOME_DIR}" \
    REPO_NAME="${REPO_NAME}" \
    GITHUB_URL="${GITHUB_URL}" \
    INVALID_TOKEN="${INVALID_TOKEN}" \
    BOT_TOKEN="${BOT_TOKEN}" \
    BOT_LANG="${BOT_LANG}" \
    DEBIAN_FRONTEND=noninteractive \
    APT_OPTS="-q=2 --yes"

# Prepare a directory to run with an unprivileged user
RUN chown -cR "${BOT_USER}:${BOT_GROUP}" ${BOT_HOME_DIR} && \
    usermod -d ${BOT_HOME_DIR} ${BOT_USER}

################################################################################

FROM base AS builder-deps

# Install build dependencies
RUN apt ${APT_OPTS} update && \
    apt ${APT_OPTS} --no-install-recommends install apt-utils && \
    apt ${APT_OPTS} --no-install-recommends install \
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
      python-tk

################################################################################

FROM builder-deps AS builder

# Build the code as unprivileged user
USER ${BOT_USER}
WORKDIR ${BOT_HOME_DIR}
RUN git clone --recurse-submodules ${GITHUB_URL} && \
    pip3 install --user --requirement ${REPO_NAME}/requirements.txt && \
    cd ${REPO_NAME}/sources && \
    sed -i -e "s/${INVALID_TOKEN}/${BOT_TOKEN}/g" constants.py && \
    sed -i -e "s/^\(\s\+\"INIT_LANG\"\)[^:]*:.*/\1 : \"${BOT_LANG}\",/g" constants.py && \
    chown -cR ${BOT_USER}:${BOT_GROUP} ${BOT_HOME_DIR} && \
    rm -rf ${BOT_HOME_DIR}/.cache ${BOT_HOME_DIR}/${REPO_NAME}/.git

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
WORKDIR ${BOT_HOME_DIR}/${REPO_NAME}/sources
CMD ["./entrypoint.sh"]

