variable "environment" {
  description = "Deployment environment (staging or production)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}


variable "s3_bucket" {
  description = "S3 bucket for Terraform state"
  default     = "osm-storage"
}

variable "dynamodb_table" {
  description = "DynamoDB table for Terraform state locking"
  default     = "terraform-locks"
}


# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "${var.environment}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.environment}-internet-gateway"
  }
}

# Route Table
resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.environment}-route-table"
  }
}


output "vpc_id" {
  value = aws_vpc.main.id
}

output "internet_gateway_id" {
  value = aws_internet_gateway.main.id
}

output "route_table_id" {
  value = aws_route_table.main.id
}
