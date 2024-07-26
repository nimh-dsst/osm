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

COPY docker_images/rtransparent/environment.yaml /app

# Create the environment
RUN conda env create -f environment.yaml

# Ensure the conda environment is activated
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate osm" | tee -a ~/.bashrc /etc/profile /etc/profile.d/conda.sh /etc/skel/.bashrc /etc/skel/.profile > /dev/null

RUN R -e '\
install.packages("roadoi", repos = "http://cran.us.r-project.org"); \
devtools::install_github("quest-bih/oddpub"); \
devtools::install_github("cran/crminer"); \
devtools::install_github("serghiou/metareadr"); \
devtools::install_github("serghiou/rtransparent", build_vignettes = F)'

# # Copy the project files and install the package
COPY docker_images/rtransparent/app.py /app

# Make entrypoint etc. convenient for users
COPY docker_images/_entrypoint.sh /usr/local/bin/_entrypoint.sh
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8071"]
