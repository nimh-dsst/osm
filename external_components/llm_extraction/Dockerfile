FROM nimhdsst/osm_base
# # Copy the project files and install the package
COPY external_components/llm_extraction/app.py /app

# Install the package
COPY osm /opt/osm/osm
RUN  export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM=9.9.9; pip install -e /opt/osm

CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8072"]
