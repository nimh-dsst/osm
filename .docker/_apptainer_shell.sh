#!/bin/bash
source ${MAMBA_ROOT_PREFIX}/etc/profile.d/conda.sh
conda activate ${ENV_NAME}
exec "\$@"
