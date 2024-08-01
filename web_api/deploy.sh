#!/bin/bash
# Script for testing the deployment during local development... ideally this
# should be done in a CI/CD pipeline but sometimes that breaks...
# 1. Run the script from the project root directory i.e. bash web_api/deploy.sh
# 2. Ensure you have the necessary environment variables set in .env
set -exu


######################################### Functions #########################################
# Function to deploy using Opentofu (fork of Terraform)
deploy_terraform() {
  local environment=$1

  pushd web_api/terraform/$environment

  # Initialize Opentofu
  echo "Initializing Opentofu..."
  tofu init

  # Plan Opentofu changes
  echo "Planning Opentofu changes..."
  tofu plan -var-file="../${environment}.tfvars"

  # Apply Opentofu changes
  echo "Applying Opentofu changes..."
  tofu apply -var-file="../${environment}.tfvars" -auto-approve

  # Get the instance ID and public DNS
  instance_id=$(tofu output -raw instance_id)
  public_dns=$(tofu output -raw public_dns)

  if [ -z "$public_dns" ]; then
    echo "Public DNS not found for $environment. Exiting..."
    exit 1
  fi

  popd

  # Deploy Docker Compose on the instance
  echo "Deploying Docker Compose on the instance..."
  ssh -o StrictHostKeyChecking=no -i $SSH_KEY_PATH ubuntu@$public_dns -p $SSH_PORT << EOF
    mkdir -p ~/app
    cd ~/app
    echo "$(<./web_api/docker-compose.yml)" > docker-compose.yml
    docker-compose up -d
EOF

  # Notify success
  if [ $? -eq 0 ]; then
    echo "Deployment to $environment environment was successful."
  else
    echo "Deployment to $environment environment failed."
  fi
}


######################################### Main Script #########################################

# Load environment variables from .env file
if [ -f .env ]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    export "$line"
  done < .env
else
  echo "No .env file found. Please create one using the .env.template file."
  exit 1
fi

# Ensure the SSH key is accessible
if [ -z "$SSH_KEY_PATH" ]; then
  echo "SSH_KEY_PATH is not set. Please set it in the .env file."
  exit 1
fi

# Log in to Docker Hub
echo "Logging in to Docker Hub..."
echo $DOCKER_HUB_ACCESS_TOKEN | docker login --username $DOCKER_HUB_USERNAME --password-stdin

# Build and push Docker image
echo "Building and pushing Docker image..."
DOCKER_BUILDKIT=1 docker build -t $DOCKER_IMAGE_TAG -f ./web_api/Dockerfile .
docker push $DOCKER_IMAGE_TAG

# Deploy
deploy_tofu ${environment}
