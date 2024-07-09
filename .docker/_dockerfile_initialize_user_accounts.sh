#!/bin/bash
set -e
addgroup --gid ${MAMBA_USER_GID} ${MAMBA_USER}
adduser --uid ${MAMBA_USER_ID} --gid ${MAMBA_USER_GID} --disabled-password --gecos "" ${MAMBA_USER}
