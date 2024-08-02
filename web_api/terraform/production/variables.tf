variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "domain" {
  description = "Domain for Traefik"
  default     = "osm.nimh.nih.gov"
}

variable "ssh_port" {
  description = "Non-standard port for SSH"
  default     = 22
}

variable "s3_bucket" {
  description = "S3 bucket for Terraform state"
  default     = "osm-storage"
}

variable "dynamodb_table" {
  description = "DynamoDB table for Terraform state locking"
  default     = "terraform-locks"
}
