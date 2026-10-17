variable "target_cloud_cluster_context" {
  type        = string
  description = "The target cloud authentication context (e.g., arn:aws:eks... or gke_project... or aks-cluster)"
  default     = "suri-multi-cloud-prod"
}

variable "deployment_region" {
  type        = string
  description = "Geographic region for regulatory compliance tracking (e.g., us-south-1 for Texas, ap-southeast-1 for Philippines)"
  default     = "us-south-1"
}
