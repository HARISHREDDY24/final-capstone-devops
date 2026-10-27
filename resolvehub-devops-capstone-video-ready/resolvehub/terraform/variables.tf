variable "aws_region" {
  description = "AWS region for ResolveHub"
  type        = string
  default     = "ap-south-1"
}
variable "project_name" {
  description = "Short project name"
  type        = string
  default     = "resolvehub"
}
variable "kubernetes_version" {
  description = "EKS Kubernetes version supported by your region"
  type        = string
  default     = "1.32"
}
variable "node_instance_type" {
  description = "EC2 instance type for EKS worker nodes"
  type        = string
  default     = "t3.medium"
}
variable "desired_nodes" {
  description = "Initial number of worker nodes"
  type        = number
  default     = 2
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "Public IP CIDRs allowed to reach the EKS API endpoint; set to your own public IP /32"
  type        = list(string)
}
