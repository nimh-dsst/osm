#!/bin/bash
eval $(/opt/conda/bin/conda shell.bash hook)
conda activate osm
exec "$@"
