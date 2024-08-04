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
    cidr_block       = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support      = true
    tags = {
        Name = "osm-vpc"
    }
}

# Subnet
resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true

  tags = {
    Name = "osm-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "osm-internet-gateway"
  }
}

# DHCP Options
resource "aws_vpc_dhcp_options" "main" {
  domain_name         = "compute-1.amazonaws.com"
  domain_name_servers = ["AmazonProvidedDNS"]

  tags = {
    Name = "osm-dhcp-options"
  }
}

resource "aws_vpc_dhcp_options_association" "main" {
  vpc_id          = aws_vpc.main.id
  dhcp_options_id = aws_vpc_dhcp_options.main.id
}

# Outputs
output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_id" {
  value = aws_subnet.main.id
}

output "internet_gateway_id" {
  value = aws_internet_gateway.main.id
}

output "route_table_id" {
  value = aws_vpc.main.main_route_table_id
}
