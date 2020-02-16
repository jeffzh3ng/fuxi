FROM ubuntu:18.04

ENV LC_ALL C.UTF-8

RUN mkdir -p /opt/fuxi
COPY . /opt/fuxi

# Init
RUN set -x \
    # You may need this if you're in Mainland China
    # && sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list \
    ###
    && apt-get update \
    && apt-get install -y python3.7 python3.7-dev python3-pip python3-setuptools \
    wget nmap curl mongodb redis-server vim net-tools git unzip \
    ruby ruby-dev \
    && python3.7 -m pip install pip==19.0.3 \
    # You may need this if you're in Mainland China
    # && python3.7 -m pip config set global.index-url 'https://pypi.tuna.tsinghua.edu.cn/simple' \
    ###
    && python3.7 -m pip install -r /opt/fuxi/requirements.txt \
    && chmod +x /opt/fuxi/migration/docker_init.sh

# Install whatweb
RUN set -x \
    && wget 'https://codeload.github.com/urbanadventurer/WhatWeb/zip/master' -O whatweb.zip \
    && unzip -q -u whatweb.zip && mv WhatWeb-master /opt/whatweb && cd /opt/whatweb \
    # You may need this if you're in Mainland China
    # && gem sources --remove 'https://rubygems.org/' \
    # && gem sources -a 'https://gems.ruby-china.com' && gem sources \
    # && gem sources -c && gem sources -u \
    ##
    && gem install bundler && bundle install \
    && ln -s /opt/whatweb/whatweb /usr/bin/whatweb


WORKDIR '/opt/fuxi'
ENTRYPOINT ["/opt/fuxi/migration/docker_init.sh"]
EXPOSE 50020