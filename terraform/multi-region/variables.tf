# 📋 Multi-Region Terraform Variables
# Tracing ID: MULTI_REGION_VARIABLES_007_20250127
# Versão: 1.0
# Data: 2025-01-27
# Objetivo: Variáveis para configuração multi-region

# Environment Configuration
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

# Region Configuration
variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
  
  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.primary_region))
    error_message = "Primary region must be a valid AWS region format."
  }
}

variable "secondary_region" {
  description = "Secondary AWS region for disaster recovery"
  type        = string
  default     = "us-west-2"
  
  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.secondary_region))
    error_message = "Secondary region must be a valid AWS region format."
  }
}

# Cluster Configuration
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "omni-keywords-finder"
  
  validation {
    condition     = length(var.cluster_name) >= 3 && length(var.cluster_name) <= 63
    error_message = "Cluster name must be between 3 and 63 characters."
  }
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
  
  validation {
    condition     = can(regex("^1\\.(2[4-9]|3[0-9])$", var.kubernetes_version))
    error_message = "Kubernetes version must be 1.24 or higher."
  }
}

# VPC Configuration - Primary Region
variable "vpc_cidr_primary" {
  description = "CIDR block for primary VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr_primary, 0))
    error_message = "Primary VPC CIDR must be a valid CIDR block."
  }
}

variable "availability_zones_primary" {
  description = "Availability zones for primary region"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnets_primary" {
  description = "Private subnet CIDR blocks for primary region"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets_primary" {
  description = "Public subnet CIDR blocks for primary region"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# VPC Configuration - Secondary Region
variable "vpc_cidr_secondary" {
  description = "CIDR block for secondary VPC"
  type        = string
  default     = "10.1.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr_secondary, 0))
    error_message = "Secondary VPC CIDR must be a valid CIDR block."
  }
}

variable "availability_zones_secondary" {
  description = "Availability zones for secondary region"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "private_subnets_secondary" {
  description = "Private subnet CIDR blocks for secondary region"
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
}

variable "public_subnets_secondary" {
  description = "Public subnet CIDR blocks for secondary region"
  type        = list(string)
  default     = ["10.1.101.0/24", "10.1.102.0/24", "10.1.103.0/24"]
}

# Database Configuration
variable "database_name" {
  description = "Name of the database"
  type        = string
  default     = "omni_keywords"
  
  validation {
    condition     = length(var.database_name) >= 1 && length(var.database_name) <= 63
    error_message = "Database name must be between 1 and 63 characters."
  }
}

variable "database_username" {
  description = "Database master username"
  type        = string
  default     = "omni_user"
  
  validation {
    condition     = length(var.database_username) >= 1 && length(var.database_username) <= 16
    error_message = "Database username must be between 1 and 16 characters."
  }
}

variable "database_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
  
  validation {
    condition     = length(var.database_password) >= 8 && length(var.database_password) <= 128
    error_message = "Database password must be between 8 and 128 characters."
  }
}

variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
  
  validation {
    condition     = can(regex("^db\\.[a-z0-9]+\\.[a-z0-9]+$", var.database_instance_class))
    error_message = "Database instance class must be a valid RDS instance class."
  }
}

variable "database_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
  
  validation {
    condition     = can(regex("^[0-9]+\\.[0-9]+$", var.database_engine_version))
    error_message = "Database engine version must be a valid version number."
  }
}

# Cache Configuration
variable "cache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
  
  validation {
    condition     = can(regex("^cache\\.[a-z0-9]+\\.[a-z0-9]+$", var.cache_node_type))
    error_message = "Cache node type must be a valid ElastiCache node type."
  }
}

# Domain Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "omni-keywords.com"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.[a-zA-Z]{2,}$", var.domain_name))
    error_message = "Domain name must be a valid domain format."
  }
}

# Monitoring Configuration
variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alarm_email))
    error_message = "Alarm email must be a valid email address."
  }
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  default     = ""
  
  validation {
    condition     = var.slack_webhook_url == "" || can(regex("^https://hooks\\.slack\\.com/services/.*$", var.slack_webhook_url))
    error_message = "Slack webhook URL must be a valid Slack webhook URL."
  }
}

# Tags Configuration
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "omni-keywords-finder"
    ManagedBy   = "terraform"
    Reliability = "multi-region"
    Environment = "production"
  }
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention days must be between 1 and 365."
  }
}

# Security Configuration
variable "enable_encryption" {
  description = "Enable encryption for all resources"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable backup for databases"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

# Scaling Configuration
variable "enable_autoscaling" {
  description = "Enable autoscaling for EKS node groups"
  type        = bool
  default     = true
}

variable "min_node_count" {
  description = "Minimum number of nodes in each node group"
  type        = number
  default     = 1
  
  validation {
    condition     = var.min_node_count >= 1 && var.min_node_count <= 10
    error_message = "Minimum node count must be between 1 and 10."
  }
}

variable "max_node_count" {
  description = "Maximum number of nodes in each node group"
  type        = number
  default     = 10
  
  validation {
    condition     = var.max_node_count >= var.min_node_count && var.max_node_count <= 50
    error_message = "Maximum node count must be greater than minimum and less than 50."
  }
}

# Network Configuration
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway for cost optimization"
  type        = bool
  default     = false
}

# SSL/TLS Configuration
variable "enable_ssl" {
  description = "Enable SSL/TLS termination"
  type        = bool
  default     = true
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate for HTTPS"
  type        = string
  default     = ""
  
  validation {
    condition     = var.ssl_certificate_arn == "" || can(regex("^arn:aws:acm:[a-z0-9-]+:[0-9]{12}:certificate/[a-zA-Z0-9-]+$", var.ssl_certificate_arn))
    error_message = "SSL certificate ARN must be a valid ACM certificate ARN."
  }
} 