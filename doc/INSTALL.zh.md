# 安装手册

你可以直接下载最新 [tar](https://github.com/jeffzh3ng/Fuxi-Scanner/tarball/master) 或者 [zip](https://github.com/jeffzh3ng/Fuxi-Scanner/zipball/master) 包 

也可以通过 `Github` 仓库获取
```bash
git clone --depth 1 https://github.com/jeffzh3ng/Fuxi-Scanner.git fuxi-scanner
```

伏羲依赖于 Python 2.7 or Python 2.6 环境

## 运行环境

安装过程演示环境为 `Ubuntu 16.04` 操作系统，其他 `Linux` 发行版可以参考

### 安装基础依赖包

```bash
sudo apt update
sudo apt install python python-dev python-pip python-setuptools nmap hydra curl
cd fuxi-scanner
sudo python -m pip install pip==9.0.3
sudo pip install -r requirements.txt
```

### 安装 MongoDB 社区版 (Ubuntu)

#### 导入Key

```bash
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
```

#### 创建源文件

Ubuntu 14.04

```bash
echo "deb https://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
```

Ubuntu 16.04

```bash
echo "deb https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
```

#### 更新软件包列表

```bash
sudo apt-get update
```

#### 安装 MongoDB.

```bash
sudo apt-get install -y mongodb-org
```

#### 运行

Start MongoDB.

```bash
sudo service mongod start
```

连接到数据库

```bash
mongo
```

创建管理员用户

```bash
use admin
db.createUser(
  {
    user: "admin",
    pwd: "14b3xfY1wd",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
```

创建扫描器用户

The following operation creates a user in the reporting database with the specified name, password, and roles

```bash
use fuxi
db.createUser(
  {
    user: "fuxi_scanner",
    pwd: "W94MRYDqOZ",
    roles: [
       { role: "readWrite", db: "fuxi"},
    ]
  }
)
```

开启认证

```bash
sudo vi /etc/mongod.conf
```

增加以下配置

```bash
security:
  authorization: "enabled"
```

重启数据库服务，设置开机启动

```bash
sudo service mongod restart
sudo systemctl enable mongod.service
```

测试认证连接

```bash
jeffzhang@ubuntu:~$ mongo
MongoDB shell version v3.6.5
connecting to: mongodb://127.0.0.1:27017
MongoDB server version: 3.6.5
> use fuxi
switched to db fuxi
> db.auth("fuxi_scanner", "W94MRYDqOZ")
1
```

返回`1`代表用户认证成功

## 扫描器配置

`fuxi-scanner` configuration files are located in the `fuxi-scanner/instance/` directory.

### 配置文件解析

```python
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    def __init__(self):
        pass

    WEB_USER = 'admin'                              #Web Auth User
    WEB_PASSWORD = 'xHmRu4sJxZ'                     #Web Auth Password
    POCSUITE_PATH = basedir + '/../fuxi/views/modules/scanner/pocsuite_plugin/'
    AWVS_REPORT_PATH = basedir + '/../fuxi/static/download/'    # static file download
    WEB_HOST = '127.0.0.1'                          #Web Server Host
    WEB_PORT = 5000                                 #Web Server Port
    UPDATE_URL = "https://fuxi.hook.ga/update"      #check update
    VERSION = '1.2.0'                               #scanner version
    AWVS_URL = 'https://192.168.56.2:3443'          #Acunetix Web Vulnerability Scanner Url
    AWVS_API_KEY = ""                               #Acunetix Web Vulnerability Scanner API Key
    

class ProductionConfig(Config):
    DB_HOST = '127.0.0.1'                           #MongoDB Host
    DB_PORT = 27017                                 #MongoDB Port (int)
    DB_NAME = 'fuxi'                                #MongoDB Name
    DB_USERNAME = 'fuxi_scanner'                    #MongoDB User
    DB_PASSWORD = 'W94MRYDqOZ'                      #MongoDB Password

    CONFIG_NAME = 'fuxi'                            #Scanner config name
    PLUGIN_DB = 'dev_plugin_info'                   #Plugin collection
    TASKS_DB = 'dev_tasks'                          #Scan tasks collection
    VULNERABILITY_DB = 'dev_vuldb'                  #Vulnerability collection
    ASSET_DB = 'dev_asset'                          #Asset collection
    CONFIG_DB = 'dev_config'                        #Scanner config collection
    SERVER_DB = 'dev_server'                        #Asset server collection
    SUBDOMAIN_DB = 'dev_subdomain'                  #Subdomain server collection
    DOMAIN_DB = 'dev_domain'                        #Domain server collection
    PORT_DB = 'dev_port_scanner'                    #Port scan collection
    AUTH_DB = 'dev_auth_tester'                     #Auth tester tasks collection
    ACUNETIX_DB = 'dev_acunetix'                    #Acunetix scanner tasks collection
    WEEKPASSWD_DB = 'dev_week_passwd'               #Week password collection
```

注意修改扫描器web服务监听的IP，默认监听本地，数据库名称、数据库用户、密码，`AWVS` 扫描器路径以及 `API Key`

## 开始使用

### 运行测试

```bash
sudo service mongod restart
cd fuxi-scanner
python migration/db_init.py
python fuxi_scanner.py
* Running on http://127.0.0.1:5000
```

一定要记得开启数据库，未报错，说明可以正常运行，打开浏览器访问`http://127.0.0.1:5000`

### 后台运行

```bash
./run.sh start      # start
./run.sh restart    # restart
./run.sh stop       # stop
```

## 使用 Caddy 进行代理 (建议)

[Caddy](https://caddyserver.com/) 服务器（或稱Caddy Web）是一个开源的，使用 Golang 编写，支持 HTTP/2 的 Web 服务端。它使用 Golang 标准库提供 HTTP 功能。

Caddy 一个显著的特性是默认启用 HTTPS。它是第一个无需额外配置即可提供 HTTPS 特性的 Web 服务器。

### 安装

- PLATFORM: Linux 64
- PLUGINS: None
- TELEMETRY: Off
- LICENSE: Personal (free)

```bash
curl https://getcaddy.com | bash -s personal
```

### 使用

[Caddy 官方用户手册](https://caddyserver.com/tutorial)

创建 caddy 文件夹

```bash
sudo mkdir /etc/caddy
sudo touch /etc/caddy/caddy.config
sudo chown -R root:www-data /etc/caddy
sudo vi /etc/caddy/caddy.config
```

编写 Caddyfile 配置文件：

[配置文件语法说明](https://caddyserver.com/docs/caddyfile)


```config
www.example.com {
    log /var/log/caddy_fuxi.log
    proxy / 127.0.0.1:5000 {
        transparent 
    }
}
```

创建 SSL 证书路径

```bash
sudo mkdir /etc/ssl/caddy
sudo chown -R www-data:root /etc/ssl/caddy
sudo chmod 0770 /etc/ssl/caddy
```

开始使用 Caddy

```bash
sudo caddy -conf /etc/caddy/caddy.config
```

---- The End ----
