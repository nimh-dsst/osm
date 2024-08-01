variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}


variable "domain" {
  description = "Domain for Traefik"
  default     = "pythonaisolutions.com"
}

variable "ssh_port" {
  description = "Non-standard port for SSH"
  default     = 2222
}
