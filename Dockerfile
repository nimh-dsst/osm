FROM condaforge/mambaforge:24.3.0-0
SHELL ["/bin/bash", "--login", "-c"]
# Set working directory
WORKDIR /app

# Install debugging tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy project files for installation
ENV ENV_NAME=osm
COPY environment.yaml /app

# Create the environment
RUN conda env create -f environment.yaml

# Ensure the conda environment is activated
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate osm" | tee -a ~/.bashrc /etc/profile /etc/profile.d/conda.sh /etc/skel/.bashrc /etc/skel/.profile > /dev/null

RUN R -e '\
install.packages("roadoi", repos = "http://cran.us.r-project.org"); \
devtools::install_github("quest-bih/oddpub"); \
devtools::install_github("cran/crminer"); \
devtools::install_github("serghiou/metareadr")'
COPY external /app/external
RUN R -e 'devtools::install("external/rtransparent")'

# Copy the project files and install the package
COPY pyproject.toml /app
COPY osm /app/osm
COPY .git /app/.git

# Install the package in editable mode
RUN pip install -e .

# Make entrypoint etc. convenient for users
COPY .docker/_entrypoint.sh /usr/local/bin/_entrypoint.sh
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "--", "osm"]
CMD ["--help"]
