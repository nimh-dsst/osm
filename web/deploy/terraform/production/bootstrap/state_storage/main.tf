terraform {
  required_version = ">= 1.0.0, < 2.0.0"
}

module "prod_state_bootstrap" {
  # I would like to make this path more robust using something like `path.root`
  source = "../../../modules/bootstrap/state_storage/"

  development_environment = var.development_environment
}
