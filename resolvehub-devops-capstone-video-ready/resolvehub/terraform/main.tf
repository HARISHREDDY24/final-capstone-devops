data "aws_availability_zones" "available" { state = "available" }
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.21.0"
  name = "${var.project_name}-vpc"
  cidr = "10.40.0.0/16"
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnets = ["10.40.1.0/24", "10.40.2.0/24"]
  private_subnets = ["10.40.11.0/24", "10.40.12.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = true
  enable_dns_hostnames = true
  enable_dns_support = true
  public_subnet_tags = { "kubernetes.io/role/elb" = "1" }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = "1" }
  tags = { Project = var.project_name, ManagedBy = "Terraform" }
}
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "20.31.6"
  cluster_name = "${var.project_name}-eks"
  cluster_version = var.kubernetes_version
  cluster_endpoint_public_access = true
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
  cluster_endpoint_private_access = true
  enable_cluster_creator_admin_permissions = true
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  eks_managed_node_groups = {
    general = {
      name = "${var.project_name}-workers"
      instance_types = [var.node_instance_type]
      min_size = 1
      max_size = 3
      desired_size = var.desired_nodes
      capacity_type = "ON_DEMAND"
    }
  }
  tags = { Project = var.project_name, ManagedBy = "Terraform" }
}
