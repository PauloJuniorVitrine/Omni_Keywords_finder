# terraform/variables.tf
# Tracing ID: INFRASTRUCTURE_AS_CODE_20241219_001
# Prompt: Variáveis do Terraform para configuração de ambientes
# Ruleset: enterprise_control_layer.yaml

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "public_access_cidrs" {
  description = "CIDR blocks for public access to EKS cluster"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS nodes"
  type        = list(string)
  default     = ["t3.medium", "t3.large"]
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 5
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

# Environment-specific overrides
locals {
  environment_configs = {
    development = {
      node_desired_size        = 1
      node_max_size           = 3
      node_min_size           = 1
      database_instance_class = "db.t3.micro"
      redis_node_type         = "cache.t3.micro"
      node_instance_types     = ["t3.medium"]
    }
    staging = {
      node_desired_size        = 2
      node_max_size           = 4
      node_min_size           = 1
      database_instance_class = "db.t3.small"
      redis_node_type         = "cache.t3.small"
      node_instance_types     = ["t3.large"]
    }
    production = {
      node_desired_size        = 3
      node_max_size           = 10
      node_min_size           = 2
      database_instance_class = "db.t3.medium"
      redis_node_type         = "cache.t3.medium"
      node_instance_types     = ["t3.large", "t3.xlarge"]
    }
  }
  
  config = local.environment_configs[var.environment]
}

# Override variables based on environment
locals {
  node_desired_size        = local.config.node_desired_size
  node_max_size           = local.config.node_max_size
  node_min_size           = local.config.node_min_size
  database_instance_class = local.config.database_instance_class
  redis_node_type         = local.config.redis_node_type
  node_instance_types     = local.config.node_instance_types
} 