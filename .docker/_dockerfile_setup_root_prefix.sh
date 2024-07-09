#!/bin/bash
set -e
mkdir -p ${MAMBA_ROOT_PREFIX}
chown -R ${MAMBA_USER}:${MAMBA_USER} ${MAMBA_ROOT_PREFIX}
