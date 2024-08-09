FROM python:3.12.5-slim-bookworm
SHELL ["/bin/bash", "--login", "-c"]
# Set working directory
WORKDIR /app

# Create the environment
RUN pip install plotly streamlit

# # Copy the project files and install the package
COPY web_api/dashboard/dashboard.py /app

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
COPY web_api/dashboard/data /app/data
