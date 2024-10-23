variable "environment" {
  description = "The name of the environment. Usually `prod`"
  default     = "prod"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.large"
  type        = string
}
