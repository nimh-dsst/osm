terraform {
  backend "s3" {
    bucket         = "osm-storage"
    key            = "terraform/${ENVIRONMENT}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}
