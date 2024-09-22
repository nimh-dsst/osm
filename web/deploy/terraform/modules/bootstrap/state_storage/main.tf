terraform {
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "tf_state" {
  bucket = "${var.bucket_name}-${var.development_environment}"

  tags = {
    Name = "${var.bucket_name}-${var.development_environment}"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  rule {
    id     = "tf_state_${var.development_environment}"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.tf_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.tf_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "tf_locks" {
  name         = "${var.table_name}-${var.development_environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "${var.bucket_name}-${var.development_environment}"
  }
}

# data "template_file" "dynamodb_policy" {
#   template = file("${path.module}/dynamodb-policy.json.tpl")

#   vars = {
#     resource = "${aws_dynamodb_table.tf_locks.arn}"
#   }
# }

# resource "aws_iam_policy" "tf_locks" {
#   name   = "DynamoDBFullAccess-${var.development_environment}"
#   policy = data.template_file.dynamodb_policy.rendered
# }

# resource "aws_iam_policy_attachment" "tf_locks" {
#   name       = "tf_locks-${var.development_environment}"
#   policy_arn = aws_iam_policy.tf_locks.arn
#   users = [
#     # This will need to be changed before merge
#     "osm",
#   ]
# }
