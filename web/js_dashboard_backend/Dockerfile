FROM python:3.9-slim

WORKDIR /app
RUN pip install fastapi uvicorn pandas pyarrow

COPY ./web/js_dashboard_backend/ /app

COPY ./dashboard_data/matches.parquet /opt/data/matches.parquet
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
