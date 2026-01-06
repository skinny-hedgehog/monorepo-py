terraform {
  backend "s3" {
    bucket  = "skinny-hedgehog-terraform-state"
    key     = "dev/terraform.tfstate"
    region  = "us-east-1"
    profile = "sh_dev"
  }
}