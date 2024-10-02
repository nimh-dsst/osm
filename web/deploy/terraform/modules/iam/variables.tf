variable "environment" {
  description = "The name of the environment. Usually `shared`, `stage`, or `prod`."
  type        = string
}

variable "region" {
  description = "AWS region"
  default     = "us-east-1"
  type        = string
}

variable "cd_iam_policy_name" {
  description = "The name of the IAM policy for continuous deployment to ECR"
  default     = "GitHubActions-ECR"
  type        = string
}

variable "cd_iam_policy_resource" {
  description = "The arn of the resource to which the IAM policy is applied"
  type        = string
}

variable "cd_iam_role_policy_name" {
  description = "The name of the IAM role policy for continuous deployment to ECR"
  default     = "github-actions-role"
  type        = string
}
