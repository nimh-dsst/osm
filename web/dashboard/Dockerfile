ARG BASE_IMAGE=osm/osm_base
FROM ${BASE_IMAGE}
COPY web/dashboard/ /app
ENV LOCAL_DATA_PATH=/opt/data/matches.parquet
CMD ["python", "app.py"]
