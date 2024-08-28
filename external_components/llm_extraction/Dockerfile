FROM nimhdsst/osm_base
# # Copy the project files and install the package
COPY external_components/llm_extraction/app.py /app

CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8072"]
