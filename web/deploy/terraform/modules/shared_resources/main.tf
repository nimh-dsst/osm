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
variable "ssh_port" {
  description = "Non-standard port for SSH"
  default     = 22
}


# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
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
  route {
    ipv6_cidr_block = "::/0"
    gateway_id      = aws_internet_gateway.main.id
  }
  tags = {
    Name = "osm-route-table"
  }
}

# Network ACL
resource "aws_network_acl" "allow_all" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "allow_all_acl"
  }
}

resource "aws_network_acl_rule" "allow_all_inbound" {
  network_acl_id = aws_network_acl.allow_all.id
  rule_number    = 100
  protocol       = "-1" # -1 means all protocols
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 65535
}

resource "aws_network_acl_rule" "allow_all_outbound" {
  network_acl_id = aws_network_acl.allow_all.id
  rule_number    = 200
  protocol       = "-1" # -1 means all protocols
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 65535
}
resource "aws_security_group" "allow_all" {
  name        = "allow_all_security_group"
  description = "Security group that allows all inbound and outbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "6"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "6"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "17"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "17"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_all_security_group"
  }
}

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


# main Subnet
resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "main-subnet"
  }
}

# Route Table Association for main
resource "aws_route_table_association" "main" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.main.id
}

# Associate the Network ACL with the Subnet
resource "aws_network_acl_association" "main" {
  subnet_id      = aws_subnet.main.id
  network_acl_id = aws_network_acl.allow_all.id
}


# Security Group


# Data source to find the latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}




# Outputs
output "vpc_id" {
  value = aws_vpc.main.id
}
output "subnet_id" {
  value = aws_subnet.main.id
}
output "security_group_id" {
  value = aws_security_group.allow_all.id
}
output "internet_gateway_id" {
  value = aws_internet_gateway.main.id
}
output "route_table_id" {
  value = aws_route_table.main.id
}
output "aws_network_acl_id" {
  value = aws_network_acl.allow_all.id
}
output "ami_id" {
  value = data.aws_ami.ubuntu.id
}
