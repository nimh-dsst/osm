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
