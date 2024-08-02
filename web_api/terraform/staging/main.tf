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
  source = "../modules/shared_resources"
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
  key_name               = "dsst2023"
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
