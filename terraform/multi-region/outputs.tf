# 📋 Multi-Region Terraform Outputs
# Tracing ID: MULTI_REGION_OUTPUTS_008_20250127
# Versão: 1.0
# Data: 2025-01-27
# Objetivo: Outputs para configuração multi-region

# EKS Cluster Outputs
output "eks_cluster_primary_name" {
  description = "Name of the primary EKS cluster"
  value       = module.eks_primary.cluster_name
}

output "eks_cluster_primary_endpoint" {
  description = "Endpoint for the primary EKS cluster"
  value       = module.eks_primary.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_primary_certificate_authority_data" {
  description = "Certificate authority data for the primary EKS cluster"
  value       = module.eks_primary.cluster_certificate_authority_data
  sensitive   = true
}

output "eks_cluster_secondary_name" {
  description = "Name of the secondary EKS cluster"
  value       = module.eks_secondary.cluster_name
}

output "eks_cluster_secondary_endpoint" {
  description = "Endpoint for the secondary EKS cluster"
  value       = module.eks_secondary.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_secondary_certificate_authority_data" {
  description = "Certificate authority data for the secondary EKS cluster"
  value       = module.eks_secondary.cluster_certificate_authority_data
  sensitive   = true
}

# VPC Outputs
output "vpc_primary_id" {
  description = "ID of the primary VPC"
  value       = module.vpc_primary.vpc_id
}

output "vpc_primary_cidr_block" {
  description = "CIDR block of the primary VPC"
  value       = module.vpc_primary.vpc_cidr_block
}

output "vpc_primary_private_subnets" {
  description = "Private subnet IDs of the primary VPC"
  value       = module.vpc_primary.private_subnets
}

output "vpc_primary_public_subnets" {
  description = "Public subnet IDs of the primary VPC"
  value       = module.vpc_primary.public_subnets
}

output "vpc_secondary_id" {
  description = "ID of the secondary VPC"
  value       = module.vpc_secondary.vpc_id
}

output "vpc_secondary_cidr_block" {
  description = "CIDR block of the secondary VPC"
  value       = module.vpc_secondary.vpc_cidr_block
}

output "vpc_secondary_private_subnets" {
  description = "Private subnet IDs of the secondary VPC"
  value       = module.vpc_secondary.private_subnets
}

output "vpc_secondary_public_subnets" {
  description = "Public subnet IDs of the secondary VPC"
  value       = module.vpc_secondary.public_subnets
}

# Database Outputs
output "database_primary_endpoint" {
  description = "Primary database endpoint"
  value       = module.rds_multi_region.primary_endpoint
  sensitive   = true
}

output "database_primary_port" {
  description = "Primary database port"
  value       = module.rds_multi_region.primary_port
}

output "database_secondary_endpoint" {
  description = "Secondary database endpoint"
  value       = module.rds_multi_region.secondary_endpoint
  sensitive   = true
}

output "database_secondary_port" {
  description = "Secondary database port"
  value       = module.rds_multi_region.secondary_port
}

output "database_connection_strings" {
  description = "Database connection strings for all regions"
  value = {
    primary   = "postgresql://${var.database_username}:${var.database_password}@${module.rds_multi_region.primary_endpoint}:${module.rds_multi_region.primary_port}/${var.database_name}"
    secondary = "postgresql://${var.database_username}:${var.database_password}@${module.rds_multi_region.secondary_endpoint}:${module.rds_multi_region.secondary_port}/${var.database_name}"
  }
  sensitive = true
}

# Cache Outputs
output "cache_primary_endpoint" {
  description = "Primary cache endpoint"
  value       = module.elasticache_multi_region.primary_endpoint
  sensitive   = true
}

output "cache_primary_port" {
  description = "Primary cache port"
  value       = module.elasticache_multi_region.primary_port
}

output "cache_secondary_endpoint" {
  description = "Secondary cache endpoint"
  value       = module.elasticache_multi_region.secondary_endpoint
  sensitive   = true
}

output "cache_secondary_port" {
  description = "Secondary cache port"
  value       = module.elasticache_multi_region.secondary_port
}

output "cache_connection_strings" {
  description = "Cache connection strings for all regions"
  value = {
    primary   = "redis://${module.elasticache_multi_region.primary_endpoint}:${module.elasticache_multi_region.primary_port}"
    secondary = "redis://${module.elasticache_multi_region.secondary_endpoint}:${module.elasticache_multi_region.secondary_port}"
  }
  sensitive = true
}

# Load Balancer Outputs
output "alb_primary_dns_name" {
  description = "DNS name of the primary Application Load Balancer"
  value       = module.alb_primary.alb_dns_name
}

output "alb_primary_zone_id" {
  description = "Zone ID of the primary Application Load Balancer"
  value       = module.alb_primary.alb_zone_id
}

output "alb_primary_arn" {
  description = "ARN of the primary Application Load Balancer"
  value       = module.alb_primary.alb_arn
}

output "alb_secondary_dns_name" {
  description = "DNS name of the secondary Application Load Balancer"
  value       = module.alb_secondary.alb_dns_name
}

output "alb_secondary_zone_id" {
  description = "Zone ID of the secondary Application Load Balancer"
  value       = module.alb_secondary.alb_zone_id
}

output "alb_secondary_arn" {
  description = "ARN of the secondary Application Load Balancer"
  value       = module.alb_secondary.alb_arn
}

# Route53 Outputs
output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = module.route53_multi_region.zone_id
}

output "route53_name_servers" {
  description = "Route53 name servers"
  value       = module.route53_multi_region.name_servers
}

output "application_domain" {
  description = "Application domain name"
  value       = var.domain_name
}

output "api_domain" {
  description = "API domain name"
  value       = "api.${var.domain_name}"
}

output "metrics_domain" {
  description = "Metrics domain name"
  value       = "metrics.${var.domain_name}"
}

# Backup Outputs
output "backup_bucket_name" {
  description = "Name of the S3 backup bucket"
  value       = module.s3_multi_region_backup.bucket_name
}

output "backup_bucket_arn" {
  description = "ARN of the S3 backup bucket"
  value       = module.s3_multi_region_backup.bucket_arn
}

output "backup_bucket_region" {
  description = "Region of the S3 backup bucket"
  value       = module.s3_multi_region_backup.bucket_region
}

# Monitoring Outputs
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.cloudwatch_multi_region.log_group_name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = module.cloudwatch_multi_region.log_group_arn
}

output "prometheus_endpoint" {
  description = "Prometheus endpoint for monitoring"
  value       = "https://prometheus.${var.domain_name}"
}

output "grafana_endpoint" {
  description = "Grafana endpoint for monitoring"
  value       = "https://grafana.${var.domain_name}"
}

# Security Outputs
output "security_group_ids" {
  description = "Security group IDs for the application"
  value = {
    primary   = module.vpc_primary.default_security_group_id
    secondary = module.vpc_secondary.default_security_group_id
  }
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for encryption"
  value       = module.rds_multi_region.kms_key_arn
  sensitive   = true
}

# Kubernetes Configuration Outputs
output "kubeconfig_primary" {
  description = "Kubeconfig for the primary cluster"
  value = {
    apiVersion = "v1"
    kind       = "Config"
    clusters = [
      {
        name = module.eks_primary.cluster_name
        cluster = {
          server                   = module.eks_primary.cluster_endpoint
          certificate-authority-data = module.eks_primary.cluster_certificate_authority_data
        }
      }
    ]
    contexts = [
      {
        name = module.eks_primary.cluster_name
        context = {
          cluster = module.eks_primary.cluster_name
          user    = module.eks_primary.cluster_name
        }
      }
    ]
    users = [
      {
        name = module.eks_primary.cluster_name
        user = {
          exec = {
            apiVersion = "client.authentication.k8s.io/v1beta1"
            command    = "aws"
            args = [
              "eks",
              "get-token",
              "--cluster-name",
              module.eks_primary.cluster_name,
              "--region",
              var.primary_region
            ]
          }
        }
      }
    ]
  }
  sensitive = true
}

output "kubeconfig_secondary" {
  description = "Kubeconfig for the secondary cluster"
  value = {
    apiVersion = "v1"
    kind       = "Config"
    clusters = [
      {
        name = module.eks_secondary.cluster_name
        cluster = {
          server                   = module.eks_secondary.cluster_endpoint
          certificate-authority-data = module.eks_secondary.cluster_certificate_authority_data
        }
      }
    ]
    contexts = [
      {
        name = module.eks_secondary.cluster_name
        context = {
          cluster = module.eks_secondary.cluster_name
          user    = module.eks_secondary.cluster_name
        }
      }
    ]
    users = [
      {
        name = module.eks_secondary.cluster_name
        user = {
          exec = {
            apiVersion = "client.authentication.k8s.io/v1beta1"
            command    = "aws"
            args = [
              "eks",
              "get-token",
              "--cluster-name",
              module.eks_secondary.cluster_name,
              "--region",
              var.secondary_region
            ]
          }
        }
      }
    ]
  }
  sensitive = true
}

# Deployment Instructions
output "deployment_instructions" {
  description = "Instructions for deploying the application"
  value = <<-EOT
    # Multi-Region Deployment Instructions
    
    ## 1. Configure kubectl for primary cluster
    aws eks update-kubeconfig --name ${module.eks_primary.cluster_name} --region ${var.primary_region}
    
    ## 2. Deploy to primary region
    kubectl apply -f k8s/multi-region/ -n omni-keywords
    
    ## 3. Configure kubectl for secondary cluster
    aws eks update-kubeconfig --name ${module.eks_secondary.cluster_name} --region ${var.secondary_region}
    
    ## 4. Deploy to secondary region
    kubectl apply -f k8s/multi-region/ -n omni-keywords
    
    ## 5. Verify deployment
    kubectl get pods -n omni-keywords
    kubectl get services -n omni-keywords
    
    ## 6. Access the application
    Primary: https://${var.domain_name}
    Secondary: https://${var.domain_name} (Route53 failover)
    
    ## 7. Monitor the deployment
    Prometheus: https://prometheus.${var.domain_name}
    Grafana: https://grafana.${var.domain_name}
  EOT
}

# Cost Estimation
output "estimated_monthly_cost" {
  description = "Estimated monthly cost for the multi-region infrastructure"
  value = {
    primary_region = {
      eks_cluster     = "$500-800"
      rds_database    = "$200-400"
      elasticache     = "$100-200"
      load_balancer   = "$50-100"
      monitoring      = "$50-100"
      total           = "$900-1600"
    }
    secondary_region = {
      eks_cluster     = "$300-500"
      rds_database    = "$100-200"
      elasticache     = "$50-100"
      load_balancer   = "$30-60"
      monitoring      = "$30-60"
      total           = "$510-920"
    }
    shared_services = {
      route53         = "$10-20"
      s3_backup       = "$20-50"
      cloudwatch      = "$30-60"
      total           = "$60-130"
    }
    total_monthly = "$1470-2650"
  }
}

# Reliability Metrics
output "reliability_metrics" {
  description = "Expected reliability metrics for the multi-region setup"
  value = {
    availability_target = "99.9%"
    rto_target         = "< 5 minutes"
    rpo_target         = "< 1 minute"
    failover_time      = "< 30 seconds"
    data_consistency   = "Strong consistency across regions"
    disaster_recovery  = "Automatic failover with Route53"
  }
} 