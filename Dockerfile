# Use the existing ScienceBeam parser image as a base
FROM elifesciences/sciencebeam-parser:latest

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container /app folder
COPY . /app

# Install dependencies in requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose port 80 outside this container
EXPOSE 80

# Run a sample command to validate set up
CMD ["python", "osm/cli.py", "--help"]
