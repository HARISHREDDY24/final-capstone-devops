# Terraform: AWS VPC + EKS

**Cost warning:** EKS control plane, NAT Gateway, and EC2 nodes incur charges. Check current AWS pricing and quotas before applying. Destroy the stack immediately after the demonstration if you do not need it.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
aws eks update-kubeconfig --region ap-south-1 --name resolvehub-eks
kubectl get nodes
```

Replace the example `203.0.113.10/32` in `terraform.tfvars` with your actual public IP followed by `/32` before applying. The example address is reserved for documentation and will not allow your connection. Never commit credentials or `terraform.tfstate`.

```bash
terraform destroy
```
