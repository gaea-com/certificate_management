FROM python:alpine3.8

ENV WEB_DIR "/data/web"
ENV ACME_DIR "/root/.acme.sh"

WORKDIR ${WEB_DIR}
COPY requirements.txt ${WEB_DIR}/requirements.txt

RUN set -ex \
    && apk update \
    && apk add --no-cache \
        bash \
        tzdata \
    && cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && sed -i "s#\(root:.*:\)\(/bin/.*\)#\1/bin/bash#g" /etc/passwd \
        \
    && apk add --no-cache --virtual .build-deps \
        gcc \
        libgcc \
        libc-dev \
        linux-headers \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
        \
        musl-dev \
        python3-dev \
        \
    && apk add --no-cache \
        mariadb-dev \
        \
        jpeg-dev \
        zlib-dev \
        freetype-dev \
        lcms2-dev \
        openjpeg-dev \
        tiff-dev \
        tk-dev \
        tcl-dev \
        \
    && pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install gunicorn \
    && rm -rf /var/cache/apk/* \
	&& apk del .build-deps

COPY . ${WEB_DIR}/

RUN set -ex \
    && apk add --no-cache \
        curl \
#        openssl-dev \
        openssl \
#        coreutils \
        socat \
    && mkdir -p ${ACME_DIR} \
    && [ ! -f ${ACME_DIR}/acme.sh ] \
    && cd ${WEB_DIR}/acme.sh \
    && ./acme.sh --install --cert-home ${ACME_DIR}/mycerts \
    && cd - \
    && rm -rf ${WEB_DIR}/acme.sh \
    && sed -i "s/\(.*acme.*\)/# \1/g" /var/spool/cron/crontabs/root \
    \
    && chmod +x ${WEB_DIR}/scripts/sh/*.sh


VOLUME ${WEB_DIR}
VOLUME ${ACME_DIR}

EXPOSE 8000

STOPSIGNAL SIGTERM

CMD ["/data/web/scripts/sh/run_web.sh"]
