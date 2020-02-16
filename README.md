# Fuxi 2.1 - developing

![Version](https://img.shields.io/badge/Version-Alpha--v2.1-red)
[![Python](https://img.shields.io/badge/Python-3.6%20%7C%203.7-blue)](https://www.python.org/)
[![GitHub license](https://img.shields.io/badge/License-MIT-green)](https://github.com/jeffzh3ng/fuxi/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/jeffzh3ng/fuxi?style=social)](https://github.com/jeffzh3ng/fuxi/stargazers)
[![Fork](https://img.shields.io/github/forks/jeffzh3ng/fuxi?style=social)](https://github.com/jeffzh3ng/fuxi/fork)

Fuxi is cross-platform compatible and works in any Python 3.x environment including Linux, Mac OSX and Windows.

## Getting Started

### Docker

```shell
docker pull jeffzh3ng/fuxi
docker run -itd --name fuxi_docker -p 5000:50020 jeffzh3ng/fuxi:latest
```

##### Wait about 15 seconds for the service to start, then visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

> - Default username: fuxi 
  - Default password: whoami
  - Application restart: `docker restart fuxi_docker`

### Installation

Dependency: `Linux` `python3.x` `redis` `mongoDB`

Get the project:

```shell
git clone https://github.com/jeffzh3ng/fuxi.git
cd fuxi
pip install -r requirements.txt
```

Creating configuration file:

```shell
cd instance/
cp _config.py config.py
vi config.py
```

Begin using `fuxi`

```shell
chmod +x fuxi_manage.sh
./fuxi_manage.sh
```

> - Default username: fuxi 
  - Default password: whoami

![demo_1](https://raw.githubusercontent.com/jeffzh3ng/fuxi/v2.1/docs/img/2020_02_06_01_demo.png)

## Issues

##### &nbsp;&nbsp;Github:&nbsp;&nbsp;&nbsp;[New issue](https://github.com/jeffzh3ng/fuxi/issues/new)
##### &nbsp;&nbsp;E-Mail:&nbsp;&nbsp;&nbsp;<jeffzh3ng@gmail.com>
##### &nbsp;&nbsp;Telegram:&nbsp;&nbsp;&nbsp;<https://t.me/jeffzh3ng>
##### &nbsp;&nbsp;WeChat:&nbsp;&nbsp;&nbsp;[QR Code](https://raw.githubusercontent.com/jeffzh3ng/fuxi/v2.1/docs/img/wechat.jpeg)
*Feel free to contact me if you have any questions or suggestions.*