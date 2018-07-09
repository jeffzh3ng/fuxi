# Fuxi-Scanner

[![Travis](https://img.shields.io/badge/Python-2.6%7C2.7-blue.svg)](https://www.python.org/)
[![GitHub license](https://img.shields.io/github/license/jeffzh3ng/Fuxi-Scanner.svg)](https://github.com/jeffzh3ng/Fuxi-Scanner/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/jeffzh3ng/Fuxi-Scanner.svg)](https://github.com/jeffzh3ng/Fuxi-Scanner/stargazers)


### README English | [中文](doc/README.zh.md)

Fuxi Scanner is an open source network security vulnerability scanner, it comes with multiple functions.

- Vulnerability detection & management
- Authentication Tester
- IT asset discovery & management
- Port scanner
- Subdomain scanner
- Acunetix Scanner (Integrate Acunetix API)

## Screenshots

![fuxi_dashboard.png](doc/images/fuxi_dashboard.png)

## Quick Start

```bash
git clone --depth 1 https://github.com/jeffzh3ng/Fuxi-Scanner.git fuxi-scanner
cd fuxi-scanner
docker build -t jeffzh3ng/fuxi-scanner .
```

or

```bash
docker pull jeffzh3ng/fuxi-scanner
```

```bash
docker run -dit -p 5000:5000 -v /opt/data:/data jeffzh3ng/fuxi-scanner:latest
```

or

```bash
docker run -dit -p 5000:5000 -v /opt/data:/data -v /etc/localtime:/etc/localtime jeffzh3ng/fuxi-scanner
// Synchronize timezone from host to container
```

Done! Wait 10s, Open your browser to `http://127.0.0.1:5000` to see it working

`password: whoami`

## Installation

[Documentation](doc/INSTALL.en.md)

## Usage

### Vulnerability Scanner

The scanner module integrate an open-sourced remote vulnerability testing and PoC development framework - [Pocsuite](https://github.com/knownsec/Pocsuite)

Like Metasploit, it is a development kit for pentesters to develope their own exploits. Based on Pocsuite, you can write the most core code of PoC/Exp without caring about the resulting output etc. There are at least several hundred people writing PoC/Exp based on Pocsuite up to date.

Some plugins in the [tests](tests/pocsuite_plugin) directory, which are updated from time to time. You can acquiring PoC scripts from [Seebug community](https://www.seebug.org/)

The target can be IP, network segment or URL.

![fuxi_poc_new_scan.png](doc/images/fuxi_poc_new_scan.png)

You can manage plugins in the Plugin Manager modules. The plugin must conform to the [PoC Coding Style](https://github.com/knownsec/Pocsuite/blob/master/docs/CODING.md)

![fuxi_poc_plugin_management.png](doc/images/fuxi_poc_plugin_management.png)

### Asset Management

IT Asset Registration:

![fuxi_asset_new.png](doc/images/fuxi_asset_new.png)

Automatic Service Discovery:

![fuxi_asset_server_search.png](doc/images/fuxi_asset_service_search.png)

You can scan the vulnerability by searching and filtering out specific services

### Authentication Tester

This is an auth tester with [hydra](https://github.com/vanhauser-thc/thc-hydra)

Currently this tool supports the following protocols: Asterisk, AFP, Cisco AAA, Cisco auth, Cisco enable, CVS, Firebird, FTP, HTTP-FORM-GET, HTTP-FORM-POST, HTTP-GET, HTTP-HEAD, HTTP-POST, HTTP-PROXY, HTTPS-FORM-GET, HTTPS-FORM-POST, HTTPS-GET, HTTPS-HEAD, HTTPS-POST, HTTP-Proxy, ICQ, IMAP, IRC, LDAP, MS-SQL, MYSQL, NCP, NNTP, Oracle Listener, Oracle SID, Oracle, PC-Anywhere, PCNFS, POP3, POSTGRES, RDP, Rexec, Rlogin, Rsh, RTSP, SAP/R3, SIP, SMB, SMTP, SMTP Enum, SNMP v1+v2+v3, SOCKS5, SSH (v1 and v2), SSHKEY, Subversion, Teamspeak (TS2), Telnet, VMware-Auth, VNC and XMPP. (55)

![fuxi_auth_new_scan.png](doc/images/fuxi_auth_new_scan.png)

### Subdomain Scanner

It helps penetration testers and bug hunters collect and gather subdomains for the domain they are targeting

You can improved wordlist in settings for finding more subdomains

![fuxi_domain_new_scan.png](doc/images/fuxi_domain_new_scan.png)

![fuxi_poc_list.png](doc/images/fuxi_domain_list.png)

### Acunetix Scanner

This module delivers scanning tasks by integrate Acunetix Web Vulnerability Scanner API

![fuxi_acunetix_new_scan.png](doc/images/fuxi_acunetix_new_scan.png)

You can scan multiple websites at the same time

### Port Scanner

Port scanner allows you to discover which TCP ports are open on your target host.

Port scanning is usually done in the initial phase of a penetration test in order to discover all network entry points into the target system

![fuxi_port_scanner.png](doc/images/fuxi_port_scanner.png)

### Settings

![fuxi_settings.png](doc/images/fuxi_settings.png)

## Links

- Homepage: [https://fuxi-scanner.com](https://fuxi-scanner.com)
- Download: [.tar](https://github.com/jeffzh3ng/Fuxi-Scanner/tarball/master) or [.zip](https://github.com/jeffzh3ng/Fuxi-Scanner/zipball/master)
- E-mail: [jeffzh3ng@gmail.com](mailto:jeffzh3ng@gmail.com)
- Telegram: [jeffzhang](https://t.me/jeffzhang)
- WeChat: [jeffzhang](https://fuxi-scanner.com/static/images/wx_20180605112603.jpg)
