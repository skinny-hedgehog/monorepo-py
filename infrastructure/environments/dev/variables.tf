variable "aws_region" {
  type        = string
  description = "AWS region for resources"
}

variable "environment" {
  type        = string
  description = "Environment (dev/staging/prod)"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
}