Guidance for deployment using Terraform and Docker Compose and GitHub Actions.

### Files and Specifications

1. **Terraform Configuration**
   - **Purpose**: Provision EC2 instances and related infrastructure for the application and Traefik, with separate configurations for staging and production.
   - **Resources**:
     - EC2 instance (reserved instance) running Ubuntu.
     - Security groups to allow necessary traffic (HTTPS and SSH on a non-standard port).
     - Subnet configuration to place the instance in the correct network.
     - DynamoDB table for Terraform state locking.

2. **Docker Compose Configuration**
   - **Purpose**: Manage the deployment of the application and Traefik on the EC2 instance.
   - **Services**:
     - **Traefik**: Acts as a TLS termination proxy, handling HTTPS traffic and forwarding it to the application.
     - **Application**: The main application service running the Docker container built from the Dockerfile.

3. **Terraform Backend Configuration**
   - **Purpose**: Configure Terraform to use an S3 bucket for state storage and a DynamoDB table for state locking.
   - **Resources**:
     - S3 bucket configuration for storing Terraform state files.
     - DynamoDB table for state locking.

4. **Deployment Script (deploy.py)**
   - **Purpose**: Automate the deployment process for local development (staging environment).
   - **Steps**:
     - Set environment variables.
     - Log in to Docker Hub.
     - Build and push the Docker image.
     - Initialize and apply Terraform configuration.
     - Deploy Docker Compose configuration on the provisioned EC2 instance.

5. **GitHub Actions Workflow (deploy.yml)**
   - **Purpose**: Formal and automated deployment for staging and production environments.
   - **Steps**:
     - Checkout code.
     - Log in to Docker Hub.
     - Build and push the Docker image.
     - Initialize and apply Terraform configuration.
     - Deploy Docker Compose configuration on the provisioned EC2 instance.
