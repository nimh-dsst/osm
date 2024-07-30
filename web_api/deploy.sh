#!/bin/bash

# Set your variables here

# Export AWS credentials
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

# Log in to Docker Hub
echo "Logging in to Docker Hub..."
echo $DOCKER_HUB_ACCESS_TOKEN | docker login --username $DOCKER_HUB_USERNAME --password-stdin

# Build and push Docker image
echo "Building and pushing Docker image..."
DOCKER_BUILDKIT=1 docker build -t $DOCKER_IMAGE_TAG -f ./web_api/docker_images/web_api/Dockerfile .
docker push $DOCKER_IMAGE_TAG

# Set up Terraform
echo "Setting up Terraform..."
terraform -install-autocomplete

# Initialize Terraform
echo "Initializing Terraform..."
terraform init -backend-config="./web_api/terraform/backend-config.tf"

# Plan Terraform changes
echo "Planning Terraform changes..."
terraform plan -var-file="./web_api/terraform/$ENVIRONMENT.tfvars"

# Apply Terraform changes
echo "Applying Terraform changes..."
terraform apply -var-file="./web_api/terraform/$ENVIRONMENT.tfvars" -auto-approve

# Get the instance ID and public DNS
instance_id=$(terraform output -raw instance_id)
public_dns=$(terraform output -raw public_dns)

# Deploy Docker Compose on the instance
echo "Deploying Docker Compose on the instance..."
ssh -o StrictHostKeyChecking=no -i dsst2023.pem ubuntu@$public_dns -p 2222 << EOF
  mkdir -p ~/app
  cd ~/app
  echo "$(<./web_api/docker-compose.yml)" > docker-compose.yml
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
