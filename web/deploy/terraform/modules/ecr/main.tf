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
  region = var.region
}

resource "aws_ecr_repository" "main" {
  name                 = "${var.ecr_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_iam_policy" "cd" {
  name = "${var.cd_iam_policy_name}-${var.environment}"
  policy = templatefile(
    "${path.module}/policies/gha-policy.json.tftpl",
    {
      resource = aws_ecr_repository.main.arn
    },
  )
}

resource "aws_iam_role" "cd" {
  name               = "${var.cd_iam_role_policy_name}-${var.environment}"
  assume_role_policy = file("${path.module}/policies/assume-role.json")
}

resource "aws_iam_role_policy_attachment" "cd" {
  role       = aws_iam_role.cd.name
  policy_arn = aws_iam_policy.cd.arn
}
