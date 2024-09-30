variable "environment" {
  description = "The name of the environment. Usually `shared`, `stage`, or `prod`."
  default     = "shared"
  type        = string
}
