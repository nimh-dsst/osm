#!/bin/bash
# Script for testing the deployment during local development... ideally this
# should be done in a CI/CD pipeline but sometimes that breaks...
# 1. Run the script from the project root directory i.e. bash web_api/deploy.sh
# 2. Ensure you have the necessary environment variables set in .env
set -eux
# Set your variables in .env (see web_api/.env.template for help)
if [ -f .env ]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    export "$line"
  done < .env
  else
    echo "No .env file found. Please create one using the .env.template file."
    exit 1
fi

echo ${SSH_KEY_PATH}

# Log in to Docker Hub
echo "Logging in to Docker Hub..."
echo $DOCKER_HUB_ACCESS_TOKEN | docker login --username $DOCKER_HUB_USERNAME --password-stdin

# Build and push Docker image
echo "Building and pushing Docker image..."
DOCKER_BUILDKIT=1 docker build -t $DOCKER_IMAGE_TAG -f ./web_api/Dockerfile .
docker push $DOCKER_IMAGE_TAG

# Set up Terraform
# echo "Setting up Terraform..."
# terraform -install-autocomplete

pushd web_api/terraform

  # Initialize Terraform
  echo "Initializing Terraform..."
  tofu init -reconfigure


  # Plan Terraform changes
  echo "Planning Terraform changes..."
  tofu plan -var-file="./$ENVIRONMENT.tfvars"

  # Apply Terraform changes
  echo "Applying Terraform changes..."
  tofu apply -var-file="./$ENVIRONMENT.tfvars" -auto-approve

  # Get the instance ID and public DNS
  instance_id=$(terraform output -raw instance_id)
  public_dns=$(terraform output -raw public_dns)
popd

# Deploy Docker Compose on the instance
echo "Deploying Docker Compose on the instance..."
ssh -o StrictHostKeyChecking=no -i $SSH_KEY_PATH ubuntu@$public_dns -p 2222 << EOF
  mkdir -p ~/app
  cd ~/app
  echo "$(<./web_api/compose.yaml)" > compose.yaml
  export ENVIRONMENT=$ENVIRONMENT
  export MONGODB_URI=$MONGODB_URI
  docker-compose up -d
EOF

# Notify success
if [ $? -eq 0 ]; then
  echo "Deployment to $ENVIRONMENT environment was successful."
else
  echo "Deployment to $ENVIRONMENT environment failed."
fi
