terraform {
  required_version = ">= 1.0.0, < 2.0.0"
}

module "stage_state" {
  source      = "./bootstrap/"
  environment = "stage"
}

module "prod_state" {
  source      = "./bootstrap/"
  environment = "prod"
}
