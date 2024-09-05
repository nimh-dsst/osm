
FROM nimhdsst/osm_base
COPY web/dashboard/ /app
ENV LOCAL_DATA_PATH=/opt/data/matches.parquet
CMD ["python", "app.py"]
