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
  source      = "../modules/shared_resources"
}

# EC2 Instance
resource "aws_instance" "staging" {
  ami                    = module.shared_resources.ami_id
  instance_type          = var.instance_type
  subnet_id              = module.shared_resources.subnet_id
  key_name               = "dsst2023"
  vpc_security_group_ids = [module.shared_resources.security_group_id]
  associate_public_ip_address = true

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

output "vpc_id" {
  value = module.shared_resources.vpc_id
}
output "internet_gateway_id" {
  value = module.shared_resources.internet_gateway_id
}
output "route_table_id" {
  value = module.shared_resources.route_table_id
}
output "network_acl_id" {
  value = module.shared_resources.aws_network_acl_id
}
output "security_group_id" {
  value = module.shared_resources.security_group_id
}
output "subnet_id" {
  value = module.shared_resources.subnet_id
}

output "instance_id" {
  value = aws_instance.staging.id
}

output "public_dns" {
  value = aws_eip.staging.public_dns
}

output "public_ip" {
  value = aws_eip.staging.public_ip
}
