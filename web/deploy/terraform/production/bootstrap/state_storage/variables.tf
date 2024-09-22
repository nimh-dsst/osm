variable "development_environment" {
  description = "The name of the development environment. Usually `stage` or `prod`. Defaults to `prod`"
  type        = string
  default     = "prod"
}
