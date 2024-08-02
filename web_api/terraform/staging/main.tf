provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket         = "osm-terraform-storage"
    key            = "terraform/staging/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}


module "shared_resources" {
  source      = "../modules/shared_resources"
}

# Staging Subnet
resource "aws_subnet" "staging" {
  vpc_id            = module.shared_resources.vpc_id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "staging-subnet"
  }
}

# Route Table Association for Staging
resource "aws_route_table_association" "staging" {
  subnet_id      = aws_subnet.staging.id
  route_table_id = module.shared_resources.route_table_id
}

# Associate the Network ACL with the Subnet
resource "aws_network_acl_association" "main" {
  subnet_id      = aws_subnet.staging.id
  network_acl_id = module.shared_resources.aws_network_acl_id
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

# Security Group
resource "aws_security_group" "staging" {
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
    ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]  # Allows ping from anywhere
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "staging-security-group"
  }
}

# Data source to find the latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

# EC2 Instance
resource "aws_instance" "staging" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.staging.id
  key_name               = "dsst2023"
  vpc_security_group_ids = [aws_security_group.staging.id]
  associate_public_ip_address = true

  tags = {
    Name = "staging-instance"
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io docker-compose
              systemctl restart sshd
              systemctl start docker
              systemctl enable docker
              EOF
}




output "instance_id" {
  value = aws_instance.staging.id
}

output "public_dns" {
  value = aws_instance.staging.public_dns
}

output "public_ip" {
  value = aws_instance.staging.public_ip
}
