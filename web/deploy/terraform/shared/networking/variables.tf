# tflint-ignore: terraform_unused_declarations
variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
  type        = string
}

# tflint-ignore: terraform_unused_declarations
variable "s3_bucket" {
  description = "S3 bucket for Terraform state"
  default     = "osm-storage"
  type        = string
}

# tflint-ignore: terraform_unused_declarations
variable "dynamodb_table" {
  description = "DynamoDB table for Terraform state locking"
  default     = "terraform-locks"
  type        = string
}

# tflint-ignore: terraform_unused_declarations
variable "ssh_port" {
  description = "Non-standard port for SSH"
  default     = 22
  type        = number
}
