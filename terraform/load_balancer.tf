# terraform/load_balancer.tf
# Tracing ID: IMP004_LOAD_BALANCER_001
# Data: 2025-01-27
# Versão: 1.0
# Status: Em Implementação

# Application Load Balancer Avançado
resource "aws_lb" "omni_keywords_advanced" {
  name               = "omni-keywords-finder-advanced-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_advanced.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = var.environment == "production"
  enable_http2               = true
  idle_timeout               = 60

  access_logs {
    bucket  = aws_s3_bucket.alb_logs.bucket
    prefix  = "alb-logs"
    enabled = true
  }

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "load-balancer"
  }
}

# Security Group para ALB Avançado
resource "aws_security_group" "alb_advanced" {
  name_prefix = "omni-keywords-finder-alb-advanced-${var.environment}"
  vpc_id      = module.vpc.vpc_id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  # Health check port
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Health check endpoint"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "load-balancer"
  }
}

# Target Group Principal
resource "aws_lb_target_group" "omni_keywords_main" {
  name     = "omni-keywords-main-${var.environment}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id

  # Health Check Avançado
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200"
    
    # Headers customizados para health check
    health_check_path = "/health"
    
    # Configurações avançadas
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }

  # Sticky Sessions
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }

  # Configurações de deregistration
  deregistration_delay = 30

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "target-group"
  }
}

# Target Group para APIs
resource "aws_lb_target_group" "omni_keywords_api" {
  name     = "omni-keywords-api-${var.environment}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id

  # Health Check específico para APIs
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    path                = "/api/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200"
  }

  # Sticky Sessions para APIs
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 300
    enabled         = true
  }

  deregistration_delay = 30

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "target-group-api"
  }
}

# Target Group para WebSocket
resource "aws_lb_target_group" "omni_keywords_websocket" {
  name     = "omni-keywords-websocket-${var.environment}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id

  # Health Check para WebSocket
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/ws/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200"
  }

  # Sticky Sessions para WebSocket
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }

  deregistration_delay = 30

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "target-group-websocket"
  }
}

# Listener HTTP (redireciona para HTTPS)
resource "aws_lb_listener" "omni_keywords_http" {
  load_balancer_arn = aws_lb.omni_keywords_advanced.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Listener HTTPS Principal
resource "aws_lb_listener" "omni_keywords_https" {
  load_balancer_arn = aws_lb.omni_keywords_advanced.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.omni_keywords.arn

  # Ação padrão - redireciona para target group principal
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.omni_keywords_main.arn
  }

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "listener"
  }
}

# Listener Rule para APIs
resource "aws_lb_listener_rule" "omni_keywords_api" {
  listener_arn = aws_lb_listener.omni_keywords_https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.omni_keywords_api.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# Listener Rule para WebSocket
resource "aws_lb_listener_rule" "omni_keywords_websocket" {
  listener_arn = aws_lb_listener.omni_keywords_https.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.omni_keywords_websocket.arn
  }

  condition {
    path_pattern {
      values = ["/ws/*"]
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "omni_keywords" {
  name                = "omni-keywords-finder-${var.environment}"
  desired_capacity    = var.min_size
  max_size            = var.max_size
  min_size            = var.min_size
  target_group_arns   = [
    aws_lb_target_group.omni_keywords_main.arn,
    aws_lb_target_group.omni_keywords_api.arn,
    aws_lb_target_group.omni_keywords_websocket.arn
  ]
  vpc_zone_identifier = module.vpc.private_subnets
  health_check_type   = "ELB"
  health_check_grace_period = 300

  # Launch Template
  launch_template {
    id      = aws_launch_template.omni_keywords.id
    version = "$Latest"
  }

  # Mixed Instances Policy
  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 1
      on_demand_percentage_above_base_capacity = 25
      spot_allocation_strategy                 = "capacity-optimized"
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.omni_keywords.id
        version           = "$Latest"
      }

      override {
        instance_type = "t3.medium"
        weighted_capacity = "1"
      }

      override {
        instance_type = "t3.large"
        weighted_capacity = "2"
      }

      override {
        instance_type = "c5.large"
        weighted_capacity = "3"
      }
    }
  }

  # Tags
  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }

  tag {
    key                 = "Project"
    value               = "omni-keywords-finder"
    propagate_at_launch = true
  }

  tag {
    key                 = "Component"
    value               = "auto-scaling-group"
    propagate_at_launch = true
  }
}

# Launch Template
resource "aws_launch_template" "omni_keywords" {
  name_prefix   = "omni-keywords-finder-${var.environment}"
  image_id      = var.ami_id
  instance_type = var.instance_type

  # User Data
  user_data = base64encode(templatefile("${path.module}/templates/user_data.sh", {
    cluster_name = aws_eks_cluster.omni_keywords.name
    region       = var.aws_region
  }))

  # IAM Instance Profile
  iam_instance_profile {
    name = aws_iam_instance_profile.omni_keywords.name
  }

  # Security Groups
  vpc_security_group_ids = [aws_security_group.eks_nodes.id]

  # Block Device Mappings
  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size           = 50
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
    }
  }

  # Monitoring
  monitoring {
    enabled = true
  }

  # Metadata Options
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
    instance_metadata_tags      = "enabled"
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Environment = var.environment
      Project     = "omni-keywords-finder"
      Component   = "launch-template"
    }
  }

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "launch-template"
  }
}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "omni_keywords_cpu" {
  name                   = "omni-keywords-cpu-policy-${var.environment}"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.omni_keywords.name
}

resource "aws_autoscaling_policy" "omni_keywords_cpu_down" {
  name                   = "omni-keywords-cpu-down-policy-${var.environment}"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.omni_keywords.name
}

# CloudWatch Alarms para Auto Scaling
resource "aws_cloudwatch_metric_alarm" "omni_keywords_cpu_high" {
  alarm_name          = "omni-keywords-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EC2 CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.omni_keywords_cpu.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.omni_keywords.name
  }
}

resource "aws_cloudwatch_metric_alarm" "omni_keywords_cpu_low" {
  alarm_name          = "omni-keywords-cpu-low-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "20"
  alarm_description   = "This metric monitors EC2 CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.omni_keywords_cpu_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.omni_keywords.name
  }
}

# CloudWatch Alarms para Load Balancer
resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  alarm_name          = "omni-keywords-alb-5xx-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors ALB 5XX errors"
  alarm_actions       = [aws_sns_topic.omni_keywords_alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.omni_keywords_advanced.arn_suffix
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_target_5xx_errors" {
  alarm_name          = "omni-keywords-alb-target-5xx-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors target 5XX errors"
  alarm_actions       = [aws_sns_topic.omni_keywords_alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.omni_keywords_advanced.arn_suffix
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_target_response_time" {
  alarm_name          = "omni-keywords-alb-target-response-time-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "2"
  alarm_description   = "This metric monitors target response time"
  alarm_actions       = [aws_sns_topic.omni_keywords_alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.omni_keywords_advanced.arn_suffix
  }
}

# S3 Bucket para logs do ALB
resource "aws_s3_bucket" "alb_logs" {
  bucket = "omni-keywords-alb-logs-${var.environment}-${random_string.bucket_suffix.result}"

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "alb-logs"
  }
}

resource "aws_s3_bucket_versioning" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    id     = "log_retention"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

# SNS Topic para alertas
resource "aws_sns_topic" "omni_keywords_alerts" {
  name = "omni-keywords-alerts-${var.environment}"

  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "alerts"
  }
}

# SNS Topic Subscription (Email)
resource "aws_sns_topic_subscription" "omni_keywords_email" {
  topic_arn = aws_sns_topic.omni_keywords_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "omni_keywords" {
  name = "omni-keywords-instance-profile-${var.environment}"
  role = aws_iam_role.omni_keywords_instance.name
}

resource "aws_iam_role" "omni_keywords_instance" {
  name = "omni-keywords-instance-role-${var.environment}"

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
    Component   = "instance-role"
  }
}

# IAM Role Policy
resource "aws_iam_role_policy" "omni_keywords_instance" {
  name = "omni-keywords-instance-policy-${var.environment}"
  role = aws_iam_role.omni_keywords_instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeRegions",
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

# Random string para nomes únicos
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Outputs
output "load_balancer_advanced_dns_name" {
  description = "DNS name of the advanced load balancer"
  value       = aws_lb.omni_keywords_advanced.dns_name
}

output "load_balancer_advanced_arn" {
  description = "ARN of the advanced load balancer"
  value       = aws_lb.omni_keywords_advanced.arn
}

output "target_group_main_arn" {
  description = "ARN of the main target group"
  value       = aws_lb_target_group.omni_keywords_main.arn
}

output "target_group_api_arn" {
  description = "ARN of the API target group"
  value       = aws_lb_target_group.omni_keywords_api.arn
}

output "autoscaling_group_name" {
  description = "Name of the auto scaling group"
  value       = aws_autoscaling_group.omni_keywords.name
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = aws_sns_topic.omni_keywords_alerts.arn
} 