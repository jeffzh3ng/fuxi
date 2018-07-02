FROM ubuntu:16.04

RUN set -x \
    && apt-get update \
    && apt-get install -y python python-dev python-pip python-setuptools nmap hydra curl apt-transport-https \
    && python -m pip install pip==9.0.3

RUN set -x \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5 \
    && echo "deb https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.6.list \
    && apt-get update \
    && apt-get install -y mongodb-org

RUN mkdir -p /opt/fuxi
COPY . /opt/fuxi

RUN set -x \
    && pip install -r /opt/fuxi/requirements.txt

WORKDIR /opt/fuxi

VOLUME ["/data"]

ENTRYPOINT ["/opt/fuxi/migration/docker_start.sh"]

EXPOSE 5000
