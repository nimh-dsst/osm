FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /app

COPY ./docker_images/web_api/requirements.txt /app/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/app/requirements.txt

# Consider installing from pypi
RUN mkdir -p /opt/osm
COPY pyproject.toml /opt/osm
COPY osm /opt/osm/osm
COPY .git /opt/osm/.git
RUN pip install  /opt/osm

COPY ./docker_images/web_api/main.py /app/app/main.py
