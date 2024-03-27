
resource "aws_secretsmanager_secret" "django_secret" {
  name        = "${var.prefix}-${var.project_name}-${var.env}-django-secret"
  description = "Django secret for ${var.project_name}"
  tags = {
    SecretPurpose = "general"
  }
}

data "aws_secretsmanager_secret_version" "django_secret" {
  secret_id  = aws_secretsmanager_secret.django_secret.id
  depends_on = [aws_secretsmanager_secret.django_secret]
}
