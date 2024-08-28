FROM nimhdsst/osm_base
RUN pip install colorcet panel
# # Copy the project files and install the package
COPY web/dashboard/ /app
CMD ["python", "app.py"]


# # Create the environment
# RUN pip install panel pymongo odmantic pandas pydantic[email] pyarrow

# ENV LOCAL_DATA_PATH=/opt/data/matches.parquet
# COPY ./tempdata/matches.parquet /opt/data/matches.parquet
