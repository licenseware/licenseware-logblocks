ARG DUMB_INIT_PATH=/usr/local/bin/dumb-init
ARG LOGCLI_PATH=/usr/local/bin/logcli
ARG BASE_IMAGE_REPO=python
ARG BASE_IMAGE_TAG=3.11-alpine

FROM curlimages/curl AS binaries

USER root

ARG DUMB_INIT_PATH
ARG LOGCLI_PATH
ARG DUMB_INIT='https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64'
ARG LOGCLI_URL='https://github.com/grafana/loki/releases/download/v2.7.1/logcli-linux-amd64.zip'

RUN curl -sSLo ${DUMB_INIT_PATH} ${DUMB_INIT} && \
    chmod +x ${DUMB_INIT_PATH} && \
    curl -sSLo logcli.zip ${LOGCLI_URL} && \
    unzip logcli.zip -d /tmp && \
    mv /tmp/logcli-linux-amd64 ${LOGCLI_PATH}


FROM ${BASE_IMAGE_REPO}:${BASE_IMAGE_TAG} AS base

COPY --from=binaries /usr/local/bin/dumb-init /usr/local/bin/dumb-init
COPY --from=binaries /usr/local/bin/logcli /usr/local/bin/logcli

RUN pip install -U pip 'licenseware-logblocks<1'


ENTRYPOINT ["dumb-init", "--", "logblocks"]
