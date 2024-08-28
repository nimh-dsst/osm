FROM nimhdsst/osm_base

COPY ./web/api/main.py /app/app/main.py

# Install the package
COPY osm /opt/osm/osm
RUN  export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM=9.9.9; pip install -e /opt/osm


CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "80", "--root-path", "/api"]
