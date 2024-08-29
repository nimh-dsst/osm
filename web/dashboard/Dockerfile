FROM nimhdsst/osm_base

# # Copy the project files and install the package
COPY web/dashboard/ /app

# Install the package
COPY osm /opt/osm/osm
RUN  export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM=9.9.9; pip install -e /opt/osm

CMD ["python", "app.py"]


# # Create the environment
# RUN pip install panel pymongo odmantic pandas pydantic[email] pyarrow

# ENV LOCAL_DATA_PATH=/opt/data/matches.parquet
# COPY ./tempdata/matches.parquet /opt/data/matches.parquet
