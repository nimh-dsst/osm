FROM condaforge/mambaforge:24.3.0-0
SHELL ["/bin/bash", "--login", "-c"]
# Set working directory
WORKDIR /app

COPY external_components/llm_extraction/environment.yaml /app

# Create the environment
RUN conda env create -f environment.yaml

# Ensure the conda environment is activated
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate osm" | tee -a ~/.bashrc /etc/profile /etc/profile.d/conda.sh /etc/skel/.bashrc /etc/skel/.profile > /dev/null

RUN mkdir -p /opt/osm
COPY pyproject.toml /opt/osm
COPY osm /opt/osm/osm
ARG PSEUDO_VERSION=0.0.1 # strongly recommended to update based on git describe
RUN SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OSM=${PSEUDO_VERSION} pip install -e /opt/osm
RUN --mount=source=.git,target=/opt/osm/.git,type=bind pip install -e /opt/osm

# # Copy the project files and install the package
COPY external_components/llm_extraction/app.py /app

# Make entrypoint etc. convenient for users
COPY external_components/_entrypoint.sh /usr/local/bin/_entrypoint.sh
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8072"]
