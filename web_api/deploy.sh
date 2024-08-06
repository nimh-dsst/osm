#!/bin/bash
# Script for testing the deployment during local development... ideally this
# should be done in a CI/CD pipeline but sometimes that breaks...
# 1. Run the script from the project root directory i.e. bash web_api/deploy.sh
# 2. Ensure you have the necessary environment variables set in .env
set -eu

# Load environment variables from .env file
if [ -f .env ]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    export "$line"
  done < .env
else
  echo "No .env file found. Please create one using the .env.template file."
  exit 1
fi
# Error fast for missing variables
echo $ENVIRONMENT $DOCKER_HUB_USERNAME $DOCKER_HUB_ACCESS_TOKEN $DOCKER_IMAGE_TAG $SSH_KEY_PATH $SSH_KEY_PATH $TF_VAR_ssh_port $TRAEFIK_USER $TRAEFIK_PASSWORD> /dev/null

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
  tofu plan

  # Apply Opentofu changes
  echo "Applying Opentofu changes..."
  tofu apply -auto-approve

  # Get the instance ID and public DNS
  instance_id=$(tofu output -raw instance_id)
  public_dns=$(tofu output -raw public_dns)

  if [ -z "$public_dns" ]; then
    echo "Public DNS not found for $environment. Exiting..."
    exit 1
  fi

  popd

  # Transfer the docker-compose files to the remote instance
  scp -o StrictHostKeyChecking=no -i $SSH_KEY_PATH temp.yaml ubuntu@$public_dns:~/docker-compose.yaml
  scp -o StrictHostKeyChecking=no -i $SSH_KEY_PATH traefik_temp.yaml ubuntu@$public_dns:~/docker-compose-traefik.yaml
  # Deploy Docker Compose on the instance
  echo "Deploying Docker Compose on the instance..."
  ssh -o StrictHostKeyChecking=no -i $SSH_KEY_PATH ubuntu@$public_dns -p $TF_VAR_ssh_port << EOF
    sudo docker-compose -f docker-compose-traefik.yaml up -d
EOF
  ssh -o StrictHostKeyChecking=no -i $SSH_KEY_PATH ubuntu@$public_dns -p $TF_VAR_ssh_port << EOF
    sudo docker-compose up -d
EOF


  # Notify success
  if [ $? -eq 0 ]; then
    echo "Deployment to $environment environment was successful."
  else
    echo "Deployment to $environment environment failed."
  fi
}


######################################### Main Script #########################################

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

# Define the compose file content
TRAEFIK_HASHED_PASSWORD=$(openssl passwd -apr1 ${TRAEFIK_PASSWORD})
TRAEFIK_COMPOSE_FILE=$(cat <<EOF
services:
  traefik:
      image: "traefik"
      restart: always
      container_name: "traefik"
      command:
        - --api
        # - --metrics.prometheus=true
        - --providers.docker=true
        - --providers.docker.exposedbydefault=false
        - --entrypoints.http.address=:80
        - --entrypoints.https.address=:443
        - --certificatesresolvers.le.acme.email=${CERT_EMAIL}
        - --certificatesresolvers.le.acme.storage=/certificates/acme.json
        - --certificatesresolvers.le.acme.tlschallenge=true
        - --log
        - --accesslog
      labels:
        - traefik.enable=true
        - traefik.http.services.traefik-dashboard.loadbalancer.server.port=8080
        #  make traefik use this domain in http
        - traefik.http.routers.traefik-dashboard-http.entrypoints=http
        - traefik.http.routers.traefik-dashboard-http.rule=Host(\`traefik.pythonaisolutions.com\`)
        #  use the traefik public network
        - traefik.docker.network=traefik-public
        # traefik-https
        - traefik.http.routers.traefik-dashboard-https.entrypoints=https
        - traefik.http.routers.traefik-dashboard-https.rule=Host(\`traefik.pythonaisolutions.com\`)
        - traefik.http.routers.traefik-dashboard-https.tls=true
        # use the "le" (Let's Encrypt) resolver
        - traefik.http.routers.traefik-dashboard-https.tls.certresolver=le
        #  use the special traefik service api@internal with the web ui
        - traefik.http.routers.traefik-dashboard-https.service=api@internal
        #  apply the redirect middleware to the http router
        - traefik.http.middlewares.https-redirect.redirectscheme.scheme=https
        - traefik.http.middlewares.https-redirect.redirectscheme.permanent=true
        # only use middleware for redirect
        - traefik.http.routers.traefik-dashboard-http.middlewares=https-redirect
        #  enable basic auth
        - traefik.http.middlewares.admin-auth.basicauth.users=${TRAEFIK_USER}:\'${TRAEFIK_HASHED_PASSWORD}\'
        #  enable http basic auth
        - traefik.http.routers.traefik-dashboard-https.middlewares=admin-auth
      ports:
        - 80:80
        - 443:443
      volumes:
        - "/var/run/docker.sock:/var/run/docker.sock:ro"
        - traefik-public-certificates:/certificates
      networks:
        - traefik-public


networks:
  traefik-public:
    external: true
volumes:
        traefik-public-certificates:
EOF
)

COMPOSE_FILE=$(cat <<EOF
version: '3'
services:
  osm_web_api:
    image: ${DOCKER_IMAGE_TAG}
    environment:
      - MONGODB_URI=${MONGODB_URI}
    ports:
      - "80:80"
    working_dir: /app/app
    depends_on:
      - traefik
    labels:
      - traefik.enable=true
      - traefik.http.routers.osm_web_api.loadbalancer.server.port=80
      - traefik.http.routers.osm_web_api-http.entrypoints=http
      - traefik.http.routers.osm_web_api-http.rule=Host(\`osm.pythonaisolutions.com\`)
      - traefik.docker.network=traefik-default
      # https
      - traefik.http.routers.osm_web_api-https.entrypoints=https
      - traefik.http.routers.osm_web_api-https.rule=Host(\`osm.pythonaisolutions.com\`)
      - traefik.http.routers.osm_web_api-https.tls=true
      # use the "le" (Let's Encrypt) resolver to get Let's Encrypt certificates
      - traefik.http.routers.osm_web_api-https.tls.certresolver=le
      # https-redirect middleware
      - traefik.http.middlewares.https-redirect.redirectscheme.scheme=https
      - traefik.http.middlewares.https-redirect.redirectscheme.permanent=true
      # apply the redirect middleware to the http router
      - traefik.http.routers.osm_web_api-http.middlewares=https-redirect

networks:
  traefik-public:
    external: true

EOF
)

# Create a temporary docker-compose.yaml file locally
echo "${COMPOSE_FILE}" > temp.yaml
echo "${TRAEFIK_COMPOSE_FILE}" > traefik_temp.yaml

# Deploy
deploy_terraform ${ENVIRONMENT}
# Clean up the local temporary file
rm {temp,traefik_temp}.yaml
