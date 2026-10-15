variable "aws_region" {
  description = "AWS region used for the VPC and EKS cluster."
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "Name for the EKS cluster and related resources."
  type        = string
  default     = "taskboard-eks"
}

variable "kubernetes_version" {
  description = "Kubernetes minor version offered by EKS in the selected region."
  type        = string
  default     = "1.36"
}

variable "vpc_cidr" {
  description = "CIDR range for the project VPC. Use a range that does not overlap existing networks."
  type        = string
  default     = "10.20.0.0/16"
}

variable "node_instance_type" {
  description = "EC2 instance type for each managed worker node; check availability and cost for your region."
  type        = string
  default     = "t3.medium"
}

variable "environment" {
  description = "Environment tag applied to AWS resources."
  type        = string
  default     = "dev"
}
