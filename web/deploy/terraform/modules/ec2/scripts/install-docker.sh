#!/bin/bash
apt-get update -y
apt install -y curl
apt-get install -y docker.io
curl -SL https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod a+x /usr/local/bin/docker-compose
systemctl restart sshd
systemctl start docker
systemctl enable docker
