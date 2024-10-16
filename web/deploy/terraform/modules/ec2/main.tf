terraform {
  required_version = ">= 1.8.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

terraform {
  backend "s3" {
    bucket         = "${var.state_bucket_name}-${var.environment}"
    key            = var.state_backend_key
    region         = var.state_storage_region
    dynamodb_table = "${var.state_table_name}-${var.environment}"
    encrypt        = true
  }
}

# EC2 Instance
resource "aws_instance" "deployment" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = data.terraform_remote_state.shared.outputs.subnet_id
  key_name                    = var.ec2_key_name
  vpc_security_group_ids      = [data.terraform_remote_state.shared.outputs.security_group_id]
  associate_public_ip_address = true
  root_block_device {
    volume_size = var.ec2_root_block_device_size
    volume_type = var.ec2_root_block_device_type
  }

  tags = {
    Name = var.environment
  }

  user_data = file("${path.module}/scripts/install-docker.sh")
}

resource "aws_eip" "deployment" {
  domain = var.eip_domain

  tags = {
    Name = var.environment
  }
}

resource "aws_eip_association" "deployment" {
  instance_id   = aws_instance.deployment.id
  allocation_id = aws_eip.deployment.id
}