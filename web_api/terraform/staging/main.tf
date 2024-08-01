provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket         = "osm-terraform-storage"
    key            = "terraform/production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}

module "shared_resources" {
  source      = "../modules/shared_resources"
  environment = "production"
}

# Production Subnet
resource "aws_subnet" "production" {
  vpc_id            = module.shared_resources.vpc_id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "production-subnet"
  }
}

# Route Table Association for Production
resource "aws_route_table_association" "production" {
  subnet_id      = aws_subnet.production.id
  route_table_id = module.shared_resources.route_table_id
}

# Security Group
resource "aws_security_group" "production" {
  vpc_id = module.shared_resources.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = var.ssh_port
    to_port     = var.ssh_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "production-security-group"
  }
}

# EC2 Instance
resource "aws_instance" "production" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.production.id
  key_name               = "dsst2023"
  vpc_security_group_ids = [aws_security_group.production.id]

  tags = {
    Name = "production-instance"
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io docker-compose
              systemctl start docker
              systemctl enable docker
              EOF
}

# Elastic IP for Production
resource "aws_eip" "production" {
  vpc = true

  tags = {
    Name = "production-elastic-ip"
  }
}

resource "aws_eip_association" "production" {
  instance_id   = aws_instance.production.id
  allocation_id = aws_eip.production.id
}

output "instance_id" {
  value = aws_instance.production.id
}

output "public_dns" {
  value = aws_instance.production.public_dns
}
