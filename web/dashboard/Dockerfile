ARG BASE_IMAGE=osm/osm_base
FROM ${BASE_IMAGE}
COPY web/dashboard/ /app
ENV LOCAL_DATA_PATH=/opt/data/matches.parquet
COPY ./dashboard_data/matches.parquet /opt/data/matches.parquet
CMD ["streamlit", "run", "streamlit_app.py"]
