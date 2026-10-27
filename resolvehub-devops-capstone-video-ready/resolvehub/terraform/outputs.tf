output "vpc_id" {
  description = "Created VPC ID"
  value       = module.vpc.vpc_id
}
output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}
output "eks_cluster_endpoint" {
  description = "EKS API endpoint"
  value       = module.eks.cluster_endpoint
}
output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
