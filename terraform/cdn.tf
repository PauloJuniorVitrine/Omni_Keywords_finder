# terraform/cdn.tf
# Tracing ID: IMP003_CDN_IMPLEMENTATION_001
# Data: 2025-01-27
# Versão: 1.0
# Status: Em Implementação

# CloudFront Distribution para CDN
resource "aws_cloudfront_distribution" "omni_keywords_cdn" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"  # Use only North America and Europe
  
  # Configuração de origem para assets estáticos
  origin {
    domain_name = aws_s3_bucket.omni_keywords_assets.bucket_regional_domain_name
    origin_id   = "S3-omni-keywords-assets"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.omni_keywords_assets.cloudfront_access_identity_path
    }
  }
  
  # Configuração de origem para API (edge caching)
  origin {
    domain_name = aws_lb.omni_keywords.dns_name
    origin_id   = "ALB-omni-keywords-api"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
      
      origin_keepalive_timeout = 60
      origin_read_timeout      = 60
    }
    
    custom_header {
      name  = "X-Forwarded-Host"
      value = var.domain_name
    }
  }
  
  # Comportamento padrão para assets estáticos
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-omni-keywords-assets"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400    # 24 horas
    max_ttl                = 31536000 # 1 ano
    
    # Compressão automática
    compress = true
    
    # Headers de cache personalizados
    response_headers_policy_id = aws_cloudfront_response_headers_policy.omni_keywords_assets.id
  }
  
  # Comportamento para APIs (edge caching)
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-omni-keywords-api"
    
    forwarded_values {
      query_string = true
      headers      = ["Authorization", "X-Requested-With", "Content-Type"]
      cookies {
        forward = "all"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 300      # 5 minutos para APIs
    max_ttl                = 3600     # 1 hora máximo
    
    # Compressão para APIs
    compress = true
    
    # Headers de cache para APIs
    response_headers_policy_id = aws_cloudfront_response_headers_policy.omni_keywords_api.id
  }
  
  # Comportamento para assets específicos (cache longo)
  ordered_cache_behavior {
    path_pattern     = "/static/css/*"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-omni-keywords-assets"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 604800   # 1 semana
    max_ttl                = 31536000 # 1 ano
    
    compress = true
    response_headers_policy_id = aws_cloudfront_response_headers_policy.omni_keywords_assets.id
  }
  
  ordered_cache_behavior {
    path_pattern     = "/static/js/*"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-omni-keywords-assets"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 604800   # 1 semana
    max_ttl                = 31536000 # 1 ano
    
    compress = true
    response_headers_policy_id = aws_cloudfront_response_headers_policy.omni_keywords_assets.id
  }
  
  ordered_cache_behavior {
    path_pattern     = "/static/image/*"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-omni-keywords-assets"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 2592000  # 30 dias
    max_ttl                = 31536000 # 1 ano
    
    compress = true
    response_headers_policy_id = aws_cloudfront_response_headers_policy.omni_keywords_assets.id
  }
  
  # Configurações de erro
  custom_error_response {
    error_code         = 404
    response_code      = "200"
    response_page_path = "/index.html"
  }
  
  custom_error_response {
    error_code         = 403
    response_code      = "200"
    response_page_path = "/index.html"
  }
  
  # Configurações de domínio
  aliases = [var.domain_name, "www.${var.domain_name}"]
  
  # Configurações de certificado SSL
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.omni_keywords.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  # Configurações de logging
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.omni_keywords_logs.bucket_domain_name
    prefix          = "cloudfront/"
  }
  
  # Configurações de tags
  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "cdn"
  }
}

# S3 Bucket para assets estáticos
resource "aws_s3_bucket" "omni_keywords_assets" {
  bucket = "omni-keywords-finder-assets-${var.environment}-${random_string.bucket_suffix.result}"
  
  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "assets"
  }
}

# Configuração de versionamento para S3
resource "aws_s3_bucket_versioning" "omni_keywords_assets" {
  bucket = aws_s3_bucket.omni_keywords_assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configuração de encriptação para S3
resource "aws_s3_bucket_server_side_encryption_configuration" "omni_keywords_assets" {
  bucket = aws_s3_bucket.omni_keywords_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Política de bucket S3 para CloudFront
resource "aws_s3_bucket_policy" "omni_keywords_assets" {
  bucket = aws_s3_bucket.omni_keywords_assets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontAccess"
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.omni_keywords_assets.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.omni_keywords_assets.arn}/*"
      }
    ]
  })
}

# Origin Access Identity para CloudFront
resource "aws_cloudfront_origin_access_identity" "omni_keywords_assets" {
  comment = "OAI for omni-keywords-finder assets"
}

# S3 Bucket para logs do CloudFront
resource "aws_s3_bucket" "omni_keywords_logs" {
  bucket = "omni-keywords-finder-logs-${var.environment}-${random_string.bucket_suffix.result}"
  
  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "logs"
  }
}

# Configuração de lifecycle para logs
resource "aws_s3_bucket_lifecycle_configuration" "omni_keywords_logs" {
  bucket = aws_s3_bucket.omni_keywords_logs.id

  rule {
    id     = "log_retention"
    status = "Enabled"

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# Certificado SSL para domínio
resource "aws_acm_certificate" "omni_keywords" {
  provider          = aws.us-east-1
  domain_name       = var.domain_name
  validation_method = "DNS"
  
  subject_alternative_names = [
    "www.${var.domain_name}",
    "*.${var.domain_name}"
  ]
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
  }
}

# Validação do certificado
resource "aws_acm_certificate_validation" "omni_keywords" {
  provider                = aws.us-east-1
  certificate_arn         = aws_acm_certificate.omni_keywords.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# Response Headers Policy para assets
resource "aws_cloudfront_response_headers_policy" "omni_keywords_assets" {
  name = "omni-keywords-assets-headers-${var.environment}"
  
  security_headers_config {
    content_type_options {
      override = true
    }
    
    frame_options {
      frame_option = "SAMEORIGIN"
      override     = true
    }
    
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
    
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      override                   = true
    }
    
    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
  }
  
  custom_headers_config {
    items {
      header   = "Cache-Control"
      override = true
      value    = "public, max-age=31536000, immutable"
    }
    
    items {
      header   = "X-Content-Type-Options"
      override = true
      value    = "nosniff"
    }
  }
}

# Response Headers Policy para APIs
resource "aws_cloudfront_response_headers_policy" "omni_keywords_api" {
  name = "omni-keywords-api-headers-${var.environment}"
  
  security_headers_config {
    content_type_options {
      override = true
    }
    
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    
    referrer_policy {
      referrer_policy = "no-referrer"
      override        = true
    }
    
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      override                   = true
    }
    
    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
  }
  
  custom_headers_config {
    items {
      header   = "Cache-Control"
      override = true
      value    = "public, max-age=300, s-maxage=300"
    }
    
    items {
      header   = "X-Content-Type-Options"
      override = true
      value    = "nosniff"
    }
    
    items {
      header   = "X-Frame-Options"
      override = true
      value    = "DENY"
    }
  }
}

# Random string para nomes únicos de buckets
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Route53 Records para validação do certificado
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.omni_keywords.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.route53_zone_id
}

# Route53 A Record para o domínio principal
resource "aws_route53_record" "omni_keywords" {
  zone_id = var.route53_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.omni_keywords_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.omni_keywords_cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 A Record para www
resource "aws_route53_record" "omni_keywords_www" {
  zone_id = var.route53_zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.omni_keywords_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.omni_keywords_cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

# CloudWatch Alarms para monitoramento do CDN
resource "aws_cloudwatch_metric_alarm" "cdn_4xx_errors" {
  alarm_name          = "omni-keywords-cdn-4xx-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = "300"
  statistic           = "Average"
  threshold           = "5"
  alarm_description   = "CDN 4xx error rate is too high"
  
  dimensions = {
    DistributionId = aws_cloudfront_distribution.omni_keywords_cdn.id
    Region         = "Global"
  }
  
  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "cdn"
  }
}

resource "aws_cloudwatch_metric_alarm" "cdn_5xx_errors" {
  alarm_name          = "omni-keywords-cdn-5xx-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = "300"
  statistic           = "Average"
  threshold           = "2"
  alarm_description   = "CDN 5xx error rate is too high"
  
  dimensions = {
    DistributionId = aws_cloudfront_distribution.omni_keywords_cdn.id
    Region         = "Global"
  }
  
  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "cdn"
  }
}

resource "aws_cloudwatch_metric_alarm" "cdn_cache_hit_ratio" {
  alarm_name          = "omni-keywords-cdn-cache-hit-ratio-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CacheHitRate"
  namespace           = "AWS/CloudFront"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "CDN cache hit ratio is too low"
  
  dimensions = {
    DistributionId = aws_cloudfront_distribution.omni_keywords_cdn.id
    Region         = "Global"
  }
  
  tags = {
    Environment = var.environment
    Project     = "omni-keywords-finder"
    Component   = "cdn"
  }
}

# Outputs
output "cloudfront_distribution_id" {
  description = "ID da distribuição CloudFront"
  value       = aws_cloudfront_distribution.omni_keywords_cdn.id
}

output "cloudfront_domain_name" {
  description = "Nome de domínio da distribuição CloudFront"
  value       = aws_cloudfront_distribution.omni_keywords_cdn.domain_name
}

output "s3_assets_bucket_name" {
  description = "Nome do bucket S3 para assets"
  value       = aws_s3_bucket.omni_keywords_assets.bucket
}

output "s3_logs_bucket_name" {
  description = "Nome do bucket S3 para logs"
  value       = aws_s3_bucket.omni_keywords_logs.bucket
}

output "acm_certificate_arn" {
  description = "ARN do certificado ACM"
  value       = aws_acm_certificate.omni_keywords.arn
} 