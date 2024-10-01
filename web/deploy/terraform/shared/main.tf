terraform {
  required_version = ">= 1.8.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "${var.state_bucket_name}-${var.environment}"
    key            = var.state_backend_key
    region         = var.state_storage_region
    dynamodb_table = "${var.state_table_name}-${var.environment}"
    encrypt        = true
  }
}

module "networking" {
  source      = "../modules/networking/"
  environment = var.environment
}

module "ecr" {
  source      = "../modules/ecr/"
  environment = var.environment
}
