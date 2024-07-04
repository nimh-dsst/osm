# Use the official Debian Docker image as the base
FROM debian:latest

# Set working directory
WORKDIR /app

# Install system dependencies, Python, pip, networking, and debugging tools
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    libcurl4-openssl-dev \
    libssl-dev \
    iputils-ping \
    r-cran-devtools \
    net-tools \
    r-base \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
COPY install_packages.R /
RUN Rscript /install_packages.R

# Copy your project files
COPY . /app

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip in the virtual environment
RUN pip install --upgrade pip

# Install the package and its dependencies
RUN pip install -e .

# Install pre-commit (optional, remove if not needed in the container)
RUN pip install pre-commit

# Set the command to the osm command
CMD ["osm", "--help"]
