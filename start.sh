#!/bin/sh

# create SSL-certification for JupyterHub
sudo certbot certonly --standalone

# create docker network for JupyterHub 
docker network create ${DOCKER_NETWORK_NAME}

# create docker volumnes for JupyterHub
docker volume create --name ${DATA_VOLUME_HOST}
docker volume create --name ${DB_VOLUME_HOST}

# pull JupyterNotebook image 
docker pull ${DOCKER_NOTEBOOK_IMAGE}

# build compose file
docker compose build --no-cache