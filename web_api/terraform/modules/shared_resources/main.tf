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
    Name = "osm-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "osm-internet-gateway"
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
    Name = "osm-route-table"
  }
}

# Network ACL
resource "aws_network_acl" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "osm-network-acl"
  }
}

# Inbound Rule for SSH
resource "aws_network_acl_rule" "allow_ssh_inbound" {
  network_acl_id = aws_network_acl.main.id
  rule_number    = 100
  protocol       = "tcp"
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  from_port      = 22
  to_port        = 22
}

# Inbound Rule for ICMP (ping)


# Outbound Rule for All Traffic
resource "aws_network_acl_rule" "allow_all_outbound" {
  network_acl_id = aws_network_acl.main.id
  rule_number    = 100
  protocol       = "-1"  # -1 means all protocols
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 0
}

resource "aws_vpc_dhcp_options" "main" {
  domain_name          = "compute-1.amazonaws.com"
  domain_name_servers  = ["AmazonProvidedDNS"]

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

output "internet_gateway_id" {
  value = aws_internet_gateway.main.id
}

output "route_table_id" {
  value = aws_route_table.main.id
}
output "aws_network_acl_id" {
  value = aws_network_acl.main.id
}
