variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (staging or production)"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs"
  type        = list(string)
}

variable "mongodb_uri" {
  description = "MongoDB URI for state locking"
}

variable "mongodb_db" {
  description = "MongoDB Database for state locking"
}

variable "domain" {
  description = "Domain for Traefik"
  default     = "osm.nimh.nih.gov"
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
