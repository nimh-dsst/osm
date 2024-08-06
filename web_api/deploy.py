import argparse
import contextlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Template

# Load environment variables from .env file
load_dotenv()

# Required environment variables
required_env_vars = [
    "ENVIRONMENT",
    "DOCKER_HUB_USERNAME",
    "DOCKER_HUB_ACCESS_TOKEN",
    "DOCKER_IMAGE_TAG",
    "SSH_KEY_PATH",
    "TF_VAR_ssh_port",
    "TRAEFIK_USER",
    "TRAEFIK_PASSWORD",
    "CERT_EMAIL",
    "MONGODB_URI",
]

# Check if all required environment variables are set
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")


def run_command(command):
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        sys.exit(f"Command failed: {command}")


def build_and_push_docker_image():
    print("Logging in to Docker Hub...")
    run_command(
        f"echo {os.getenv('DOCKER_HUB_ACCESS_TOKEN')} | docker login --username {os.getenv('DOCKER_HUB_USERNAME')} --password-stdin"
    )

    print("Building and pushing Docker image...")
    run_command(
        f"DOCKER_BUILDKIT=1 docker build -t {os.getenv('DOCKER_IMAGE_TAG')} -f ./web_api/Dockerfile ."
    )
    run_command(f"docker push {os.getenv('DOCKER_IMAGE_TAG')}")


def deploy_terraform(environment):
    print("Deploying using Opentofu...")
    terraform_dir = f"web_api/terraform/{environment}"

    with contextlib.chdir(terraform_dir):
        run_command("tofu init")
        run_command("tofu plan")
        run_command("tofu apply -auto-approve")

        public_dns = (
            subprocess.check_output("tofu output -raw public_dns", shell=True)
            .decode()
            .strip()
        )

    if not public_dns:
        sys.exit(f"Public DNS not found for {environment}. Exiting...")

    # Write public_dns to a hidden file in the current directory
    Path(".public_dns").write_text(public_dns)


def create_temp_files():
    traefik_template_path = Path("web_api/docker-compose-traefik.yaml.j2")
    compose_template_path = Path("web_api/docker-compose.yaml.j2")

    traefik_auth = (
        subprocess.check_output(
            f"htpasswd -nb {os.getenv('TRAEFIK_USER')} {os.getenv('TRAEFIK_PASSWORD')}",
            shell=True,
        )
        .decode()
        .strip()
        .replace("$", "$$")
    )

    traefik_template = Template(traefik_template_path.read_text())
    compose_template = Template(compose_template_path.read_text())

    traefik_compose_content = traefik_template.render(
        cert_email=os.getenv("CERT_EMAIL"),
        traefik_auth=traefik_auth,
    )

    compose_content = compose_template.render(
        docker_image_tag=os.getenv("DOCKER_IMAGE_TAG"),
        mongodb_uri=os.getenv("MONGODB_URI"),
    )

    temp_dir = Path(tempfile.mkdtemp())
    traefik_compose_path = temp_dir / "docker-compose-traefik.yaml"
    compose_path = temp_dir / "docker-compose.yaml"

    traefik_compose_path.write_text(traefik_compose_content)
    compose_path.write_text(compose_content)

    return traefik_compose_path, compose_path


def transfer_and_deploy_files(public_dns, traefik_compose_path, compose_path):
    print("Transferring Docker Compose files to the remote instance...")
    ssh_key_path = os.getenv("SSH_KEY_PATH")
    ssh_port = os.getenv("TF_VAR_ssh_port")

    run_command(
        f"scp -o StrictHostKeyChecking=no -i {ssh_key_path} {compose_path} ubuntu@{public_dns}:~/docker-compose.yaml"
    )
    run_command(
        f"scp -o StrictHostKeyChecking=no -i {ssh_key_path} {traefik_compose_path} ubuntu@{public_dns}:~/docker-compose-traefik.yaml"
    )

    print("Deploying Docker Compose on the instance...")
    run_command(
        f"ssh -o StrictHostKeyChecking=no -i {ssh_key_path} ubuntu@{public_dns} -p {ssh_port} 'sudo docker-compose -f docker-compose-traefik.yaml up -d'"
    )
    run_command(
        f"ssh -o StrictHostKeyChecking=no -i {ssh_key_path} ubuntu@{public_dns} -p {ssh_port} 'sudo docker-compose up -d'"
    )


def main(skip_terraform_deployment, skip_docker_rebuild):
    if not skip_docker_rebuild:
        build_and_push_docker_image()

    traefik_compose_path, compose_path = create_temp_files()

    if not skip_terraform_deployment:
        deploy_terraform(os.getenv("ENVIRONMENT"))

    public_dns_file = Path(".public_dns")
    if public_dns_file.exists():
        public_dns = public_dns_file.read_text().strip()
        transfer_and_deploy_files(public_dns, traefik_compose_path, compose_path)

    # Clean up temporary files
    traefik_compose_path.unlink()
    compose_path.unlink()
    print("Cleaned up temporary files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy the application.")
    parser.add_argument(
        "--skip-terraform-deployment",
        action="store_true",
        help="Skip the Terraform deployment.",
    )
    parser.add_argument(
        "--skip-docker-rebuild",
        action="store_true",
        help="Skip rebuilding the Docker image.",
    )

    args = parser.parse_args()
    main(args.skip_terraform_deployment, args.skip_docker_rebuild)
