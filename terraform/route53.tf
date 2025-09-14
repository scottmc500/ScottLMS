# Route53 Hosted Zone
resource "aws_route53_zone" "scottlms" {
  name = var.domain_name

  tags = local.common_tags
}

# Route53 Records
resource "aws_route53_record" "scottlms" {
  zone_id = aws_route53_zone.scottlms.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = module.alb.lb_dns_name
    zone_id                = module.alb.lb_zone_id
    evaluate_target_health = true
  }
}

# ACM Certificate
resource "aws_acm_certificate" "scottlms" {
  domain_name       = var.domain_name
  subject_alternative_names = [
    "*.${var.domain_name}"
  ]
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.common_tags
}

# ACM Certificate Validation
resource "aws_route53_record" "scottlms_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.scottlms.domain_validation_options : dvo.domain_name => {
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
  zone_id         = aws_route53_zone.scottlms.zone_id
}

resource "aws_acm_certificate_validation" "scottlms" {
  certificate_arn         = aws_acm_certificate.scottlms.arn
  validation_record_fqdns = [for record in aws_route53_record.scottlms_cert_validation : record.fqdn]
}
