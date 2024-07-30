provider "aws" {
  region = "us-east-1"
}

variable "environment" {
  description = "The environment to deploy to (staging or production)"
  type        = string
}

variable "instance_type" {
  default = "t3.micro"
}

variable "ssh_port" {
  description = "Non-standard port for SSH"
  default     = 2222
}

variable "s3_bucket" {
  description = "S3 bucket for Terraform state"
  default     = "osm-storage"
}

variable "dynamodb_table" {
  description = "DynamoDB table for Terraform state locking"
  default     = "terraform-locks"
}

variable "domain" {
  description = "Domain for Traefik"
  default     = "osm.nimh.nih.gov"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "${var.environment}-vpc"
  }
}

resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "${var.environment}-subnet"
  }
}

resource "aws_security_group" "app" {
  vpc_id = aws_vpc.main.id

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
    Name = "${var.environment}-security-group"
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.main.id
  key_name      = "dsst2023"
  security_groups = [aws_security_group.app.id]

  tags = {
    Name = "${var.environment}-instance"
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io docker-compose
              systemctl start docker
              systemctl enable docker
              EOF
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = var.dynamodb_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "${var.environment}-terraform-locks"
  }
}
