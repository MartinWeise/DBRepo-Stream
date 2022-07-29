# JupyterHub Docker Compose

## Prerequisites
Following installation code is tested for Ubuntu and Debian.
- Docker and Docker-Compose
  - `apt install docker docker-compose`
- [Certbot](https://certbot.eff.org/) (Let's Encrypt)
  - `apt install snapd`
  - `sudo snap install core; sudo snap refresh core`
  - `sudo snap install --classic certbot`
  - `sudo ln -s /snap/bin/certbot /usr/bin/certbot`

## Installation
This repository includes a multi user JupyterHub implementation using docker-compose. Credits to [jupyterhub-deploy-docker](https://github.com/jupyterhub/jupyterhub-deploy-docker).

This deployment uses GitHub OAuth to authenticate users. For this create and register a [GitHub OAuth application](https://github.com/settings/applications/new). After that use the obtained information to create an `oauth.env` file in a secrets folder. The `oauth.env` file should look like this:

```
GITHUB_CLIENT_ID=<github_client_id>
GITHUB_CLIENT_SECRET=<github_client_secret>
OAUTH_CALLBACK_URL=https://<myhost.mydomain>/hub/oauth_callback
```

By running the `start.sh` script the whole setup process will be automatically started including:
- generating SSL-certificate from Let's Encrypt
- creating necessary docker volumes and networks
- pulling/ building JupyterHub and JupyterNotebook images

During this process you will have to fill information like domain () and email for Let's Encrypt 

## Start
By running `docker-compose up` or `docker-compose up -d` JupyterHub will be startet.

