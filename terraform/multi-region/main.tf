# 📋 Multi-Region Terraform Configuration
# Tracing ID: MULTI_REGION_TERRAFORM_006_20250127
# Versão: 1.0
# Data: 2025-01-27
# Objetivo: Infraestrutura multi-region com alta disponibilidade

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  backend "s3" {
    bucket = "omni-keywords-terraform-state"
    key    = "multi-region/terraform.tfstate"
    region = "us-east-1"
  }
}

# Provider Configuration
provider "aws" {
  region = var.primary_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "omni-keywords-finder"
      ManagedBy   = "terraform"
      Reliability = "multi-region"
    }
  }
}

provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "omni-keywords-finder"
      ManagedBy   = "terraform"
      Reliability = "multi-region"
    }
  }
}

# VPC Configuration - Primary Region
module "vpc_primary" {
  source = "./modules/vpc"
  
  region        = var.primary_region
  environment   = var.environment
  vpc_cidr      = var.vpc_cidr_primary
  cluster_name  = "${var.cluster_name}-${var.primary_region}"
  
  availability_zones = var.availability_zones_primary
  private_subnets    = var.private_subnets_primary
  public_subnets     = var.public_subnets_primary
  
  enable_nat_gateway = true
  single_nat_gateway = false
}

# VPC Configuration - Secondary Region
module "vpc_secondary" {
  source = "./modules/vpc"
  providers = {
    aws = aws.secondary
  }
  
  region        = var.secondary_region
  environment   = var.environment
  vpc_cidr      = var.vpc_cidr_secondary
  cluster_name  = "${var.cluster_name}-${var.secondary_region}"
  
  availability_zones = var.availability_zones_secondary
  private_subnets    = var.private_subnets_secondary
  public_subnets     = var.public_subnets_secondary
  
  enable_nat_gateway = true
  single_nat_gateway = false
}

# EKS Cluster - Primary Region
module "eks_primary" {
  source = "./modules/eks"
  
  cluster_name    = "${var.cluster_name}-${var.primary_region}"
  cluster_version = var.kubernetes_version
  region          = var.primary_region
  environment     = var.environment
  
  vpc_id     = module.vpc_primary.vpc_id
  subnet_ids = module.vpc_primary.private_subnets
  
  node_groups = {
    general = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 1
      
      instance_types = ["t3.medium", "t3.large"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        Environment = var.environment
        Region      = var.primary_region
        NodeGroup   = "general"
      }
      
      taints = []
    }
    
    dedicated = {
      desired_capacity = 2
      max_capacity     = 5
      min_capacity     = 1
      
      instance_types = ["t3.large", "t3.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        Environment = var.environment
        Region      = var.primary_region
        NodeGroup   = "dedicated"
      }
      
      taints = [{
        key    = "dedicated"
        value  = "omni-keywords"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}

# EKS Cluster - Secondary Region
module "eks_secondary" {
  source = "./modules/eks"
  providers = {
    aws = aws.secondary
  }
  
  cluster_name    = "${var.cluster_name}-${var.secondary_region}"
  cluster_version = var.kubernetes_version
  region          = var.secondary_region
  environment     = var.environment
  
  vpc_id     = module.vpc_secondary.vpc_id
  subnet_ids = module.vpc_secondary.private_subnets
  
  node_groups = {
    general = {
      desired_capacity = 2
      max_capacity     = 8
      min_capacity     = 1
      
      instance_types = ["t3.medium", "t3.large"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        Environment = var.environment
        Region      = var.secondary_region
        NodeGroup   = "general"
      }
      
      taints = []
    }
  }
}

# RDS Multi-Region Configuration
module "rds_multi_region" {
  source = "./modules/rds-multi-region"
  
  primary_region   = var.primary_region
  secondary_region = var.secondary_region
  
  primary_vpc_id     = module.vpc_primary.vpc_id
  secondary_vpc_id   = module.vpc_secondary.vpc_id
  primary_subnet_ids = module.vpc_primary.private_subnets
  secondary_subnet_ids = module.vpc_secondary.private_subnets
  
  database_name     = var.database_name
  database_username = var.database_username
  database_password = var.database_password
  
  instance_class = var.database_instance_class
  engine_version = var.database_engine_version
  
  backup_retention_period = 7
  multi_az               = true
  deletion_protection    = true
  
  environment = var.environment
}

# ElastiCache Multi-Region Configuration
module "elasticache_multi_region" {
  source = "./modules/elasticache-multi-region"
  
  primary_region   = var.primary_region
  secondary_region = var.secondary_region
  
  primary_vpc_id     = module.vpc_primary.vpc_id
  secondary_vpc_id   = module.vpc_secondary.vpc_id
  primary_subnet_ids = module.vpc_primary.private_subnets
  secondary_subnet_ids = module.vpc_secondary.private_subnets
  
  node_type = var.cache_node_type
  num_cache_nodes = 2
  
  environment = var.environment
}

# Application Load Balancer - Primary Region
module "alb_primary" {
  source = "./modules/alb"
  
  name        = "${var.cluster_name}-alb-${var.primary_region}"
  environment = var.environment
  region      = var.primary_region
  
  vpc_id     = module.vpc_primary.vpc_id
  subnet_ids = module.vpc_primary.public_subnets
  
  security_groups = [module.vpc_primary.default_security_group_id]
  
  enable_deletion_protection = true
  enable_http2              = true
  
  target_groups = {
    app = {
      port     = 8000
      protocol = "HTTP"
      health_check = {
        path                = "/health/ready"
        port                = "traffic-port"
        healthy_threshold   = 2
        unhealthy_threshold = 3
        timeout             = 5
        interval            = 30
      }
    }
  }
}

# Application Load Balancer - Secondary Region
module "alb_secondary" {
  source = "./modules/alb"
  providers = {
    aws = aws.secondary
  }
  
  name        = "${var.cluster_name}-alb-${var.secondary_region}"
  environment = var.environment
  region      = var.secondary_region
  
  vpc_id     = module.vpc_secondary.vpc_id
  subnet_ids = module.vpc_secondary.public_subnets
  
  security_groups = [module.vpc_secondary.default_security_group_id]
  
  enable_deletion_protection = true
  enable_http2              = true
  
  target_groups = {
    app = {
      port     = 8000
      protocol = "HTTP"
      health_check = {
        path                = "/health/ready"
        port                = "traffic-port"
        healthy_threshold   = 2
        unhealthy_threshold = 3
        timeout             = 5
        interval            = 30
      }
    }
  }
}

# Route53 Configuration for Multi-Region
module "route53_multi_region" {
  source = "./modules/route53-multi-region"
  
  domain_name = var.domain_name
  
  primary_alb_dns_name   = module.alb_primary.alb_dns_name
  primary_alb_zone_id    = module.alb_primary.alb_zone_id
  secondary_alb_dns_name = module.alb_secondary.alb_dns_name
  secondary_alb_zone_id  = module.alb_secondary.alb_zone_id
  
  primary_region   = var.primary_region
  secondary_region = var.secondary_region
  
  environment = var.environment
}

# CloudWatch Alarms for Multi-Region Monitoring
module "cloudwatch_multi_region" {
  source = "./modules/cloudwatch-multi-region"
  
  primary_region   = var.primary_region
  secondary_region = var.secondary_region
  
  environment = var.environment
  
  alarm_email = var.alarm_email
  slack_webhook_url = var.slack_webhook_url
}

# S3 Bucket for Multi-Region Backup
module "s3_multi_region_backup" {
  source = "./modules/s3-multi-region-backup"
  
  bucket_name = "${var.cluster_name}-backup-${var.environment}"
  
  primary_region   = var.primary_region
  secondary_region = var.secondary_region
  
  environment = var.environment
  
  versioning_enabled = true
  lifecycle_rules = [
    {
      id      = "backup_retention"
      enabled = true
      
      transition = [
        {
          days          = 30
          storage_class = "STANDARD_IA"
        },
        {
          days          = 90
          storage_class = "GLACIER"
        },
        {
          days          = 365
          storage_class = "DEEP_ARCHIVE"
        }
      ]
    }
  ]
} 