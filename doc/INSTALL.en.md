# Installation

You can download the latest tarball by clicking [here](https://github.com/jeffzh3ng/Fuxi-Scanner/tarball/master)  or latest zipball by clicking [here](https://github.com/jeffzh3ng/Fuxi-Scanner/zipball/master).

Preferably, you can download fuxi-scanner by cloning the Git repository:
```bash
git clone --depth 1 https://github.com/jeffzh3ng/Fuxi-Scanner.git fuxi-scanner
```

Fuxi Scanner works out of the box with [Python](https://www.python.org/) version 2.6.x and 2.7.x on any platform.

## Environment Setup

This guide should get you going on `Ubuntu` system. 

### Install the base dev packages

```bash
sudo apt update
sudo apt install python python-dev python-pip python-setuptools nmap hydra curl
cd fuxi-scanner
sudo python -m pip install pip==9.0.3
sudo pip install -r requirements.txt
```

### Install MongoDB Community Edition (Ubuntu)

#### Import the public key used by the package management system.

The Ubuntu package management tools (i.e. dpkg and apt) ensure package consistency and authenticity by requiring that distributors sign packages with GPG keys.
 
Issue the following command to import the MongoDB public GPG Key:

```bash
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
```

#### Create a list file for MongoDB.

Create the /etc/apt/sources.list.d/mongodb-org-3.6.list list file using the command appropriate for your version of Ubuntu:

Ubuntu 14.04

```bash
echo "deb https://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
```

Ubuntu 16.04

```bash
echo "deb https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
```

#### Reload local package database.

Issue the following command to reload the local package database:

```bash
sudo apt-get update
```

#### Install the MongoDB packages.

Install the latest stable version of MongoDB.

Issue the following command:

```bash
sudo apt-get install -y mongodb-org
```

#### Run MongoDB Community Edition

Start MongoDB.

Issue the following command to start mongod:

```bash
sudo service mongod start
```

Connect to the instance.

```bash
mongo
```

Create the user administrator.

In the admin database, add a user with the [userAdminAnyDatabase](https://docs.mongodb.com/manual/reference/built-in-roles/#userAdminAnyDatabase) role

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

Add Scanner Users

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

Enable Auth

```bash
sudo vi /etc/mongod.conf

security:
  authorization: "enabled"
```

```bash
sudo service mongod restart
sudo systemctl enable mongod.service
```

To authenticate after connecting

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

## Configuration Handling

`fuxi-scanner` configuration files are located in the `fuxi-scanner/instance/` directory.

### Full Example Configuration

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

## Using Fuxi-Scanner 

### Running tests

```bash
sudo service mongod restart
cd fuxi-scanner
python migration/db_init.py
python fuxi_scanner.py
* Running on http://127.0.0.1:5000
```
Done! Open your browser to `http://127.0.0.1:5000` to see it working

### Run it as background process

```bash
./run.sh start      # start
./run.sh restart    # restart
./run.sh stop       # stop
```

## Using Caddy (Optional)

[Caddy](https://caddyserver.com/), sometimes clarified as the Caddy web server, is an open source, HTTP/2-enabled web server written in Go. It uses the Go standard library for its HTTP functionality.

One of Caddy's most notable features is enabling HTTPS by default.


### Install Caddy

- PLATFORM: Linux 64
- PLUGINS: None
- TELEMETRY: Off
- LICENSE: Personal (free)

```bash
curl https://getcaddy.com | bash -s personal
```

### Using Caddy

[USER GUIDE](https://caddyserver.com/tutorial)

Create caddy folder

```bash
sudo mkdir /etc/caddy
sudo touch /etc/caddy/caddy.config
sudo chown -R root:www-data /etc/caddy
sudo vi /etc/caddy/caddy.config
```

The HTTP Caddyfile：

[Caddyfile Syntax](https://caddyserver.com/docs/caddyfile)


```config
www.example.com {
    log /var/log/caddy_fuxi.log
    proxy / 127.0.0.1:5000 {
        transparent 
    }
}
```

Create SSL certificates folder

```bash
sudo mkdir /etc/ssl/caddy
sudo chown -R www-data:root /etc/ssl/caddy
sudo chmod 0770 /etc/ssl/caddy
```

Start Caddy

```bash
sudo caddy -conf /etc/caddy/caddy.config
```

---- The End ----
