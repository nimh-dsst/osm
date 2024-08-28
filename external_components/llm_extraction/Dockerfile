FROM condaforge/mambaforge:24.3.0-0
SHELL ["/bin/bash", "--login", "-c"]
# Set working directory
WORKDIR /app

COPY external_components/rtransparent/environment.yaml /app

# Create the environment
RUN conda env create -f environment.yaml

# Ensure the conda environment is activated
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate osm" | tee -a ~/.bashrc /etc/profile /etc/profile.d/conda.sh /etc/skel/.bashrc /etc/skel/.profile > /dev/null

RUN R -e '\
devtools::install_github("quest-bih/oddpub",ref="c5b091c7e82ed6177192dc380a515b3dc6304863"); \
devtools::install_github("serghiou/rtransparent", build_vignettes = F)'

# # Copy the project files and install the package
COPY external_components/rtransparent/app.py /app

# Make entrypoint etc. convenient for users
COPY external_components/_entrypoint.sh /usr/local/bin/_entrypoint.sh
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8071"]
