# terraform/iam.tf
# Tracing ID: INFRASTRUCTURE_AS_CODE_20241219_001
# Prompt: IAM roles e políticas para EKS
# Ruleset: enterprise_control_layer.yaml

# EKS Cluster Role
resource "aws_iam_role" "eks_cluster" {
  name = "omni-keywords-finder-eks-cluster-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster.name
}

# EKS Node Group Role
resource "aws_iam_role" "eks_nodes" {
  name = "omni-keywords-finder-eks-nodes-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "ec2_container_registry_read_only" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodes.name
}

# Custom policies for application access
resource "aws_iam_policy" "eks_nodes_s3_access" {
  name        = "omni-keywords-finder-s3-access-${var.environment}"
  description = "S3 access policy for EKS nodes"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::omni-keywords-finder-*",
          "arn:aws:s3:::omni-keywords-finder-*/*"
        ]
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

resource "aws_iam_role_policy_attachment" "eks_nodes_s3_access" {
  policy_arn = aws_iam_policy.eks_nodes_s3_access.arn
  role       = aws_iam_role.eks_nodes.name
}

# ECR access policy
resource "aws_iam_policy" "eks_nodes_ecr_access" {
  name        = "omni-keywords-finder-ecr-access-${var.environment}"
  description = "ECR access policy for EKS nodes"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeRepositories",
          "ecr:ListImages"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

resource "aws_iam_role_policy_attachment" "eks_nodes_ecr_access" {
  policy_arn = aws_iam_policy.eks_nodes_ecr_access.arn
  role       = aws_iam_role.eks_nodes.name
}

# CloudWatch Logs policy
resource "aws_iam_policy" "eks_nodes_cloudwatch_logs" {
  name        = "omni-keywords-finder-cloudwatch-logs-${var.environment}"
  description = "CloudWatch Logs policy for EKS nodes"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

resource "aws_iam_role_policy_attachment" "eks_nodes_cloudwatch_logs" {
  policy_arn = aws_iam_policy.eks_nodes_cloudwatch_logs.arn
  role       = aws_iam_role.eks_nodes.name
}

# Instance profile for EKS nodes
resource "aws_iam_instance_profile" "eks_nodes" {
  name = "omni-keywords-finder-eks-nodes-${var.environment}"
  role = aws_iam_role.eks_nodes.name

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

# Security group for EKS nodes
resource "aws_security_group" "eks_nodes" {
  name_prefix = "omni-keywords-finder-eks-nodes-${var.environment}"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

# Allow all traffic within the security group
resource "aws_security_group_rule" "eks_nodes_ingress_self" {
  description              = "Allow all traffic within the security group"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.eks_nodes.id
  source_security_group_id = aws_security_group.eks_nodes.id
  type                     = "ingress"
}

# Allow traffic from ALB to EKS nodes
resource "aws_security_group_rule" "eks_nodes_ingress_alb" {
  description              = "Allow traffic from ALB"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_nodes.id
  source_security_group_id = aws_security_group.alb.id
  type                     = "ingress"
}

# Random password for database
resource "random_password" "database_password" {
  length  = 16
  special = true
  upper   = true
  lower   = true
  numeric = true
} 