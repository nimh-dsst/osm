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
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket         = "osm-terraform-storage"
    key            = "terraform/staging-state/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}


module "shared_resources" {
  source = "../modules/shared_resources"
}

# EC2 Instance
resource "aws_instance" "staging" {
  ami                         = module.shared_resources.ami_id
  instance_type               = var.instance_type
  subnet_id                   = module.shared_resources.subnet_id
  key_name                    = "dsst2023"
  vpc_security_group_ids      = [module.shared_resources.security_group_id]
  associate_public_ip_address = true
  root_block_device {
    volume_size = 30
    volume_type = "gp2" # General Purpose SSD (can be "gp2", "gp3", "io1", "io2", etc.)
  }

  tags = {
    Name = "staging-instance"
  }

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt install -y curl
    apt-get install -y docker.io
    curl -SL https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
    chmod a+x /usr/local/bin/docker-compose
    systemctl restart sshd
    systemctl start docker
    systemctl enable docker
              EOF
}

resource "aws_eip" "staging" {
  domain = "vpc"

  tags = {
    Name = "staging-elastic-ip"
  }
}

resource "aws_eip_association" "staging" {
  instance_id   = aws_instance.staging.id
  allocation_id = aws_eip.staging.id
}
