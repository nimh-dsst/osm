FROM nimhdsst/osm_base

COPY external_components/llm_extraction/app.py /app

# Install the package
COPY osm /opt/osm/osm
RUN --mount=type=cache,target=/root/.cache/uv \
    export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM=9.9.9; \
    cd /opt/osm ; uv pip install -e .
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8072"]
