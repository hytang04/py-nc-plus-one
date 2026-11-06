terraform {
  backend "s3" {
    bucket         = "nc-plus-one-terraform-state-hyt"
    key            = "nc-plus-one/terraform.tfstate"
    region         = "eu-west-2"
    encrypt        = true
  }
}