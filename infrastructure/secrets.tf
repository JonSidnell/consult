
resource "aws_secretsmanager_secret" "django_secret" {
  name        = "${var.prefix}-${var.project_name}-${var.env}-django-secret"
  description = "Django secret for ${var.project_name}"
  tags = {
    SecretPurpose = "general" # pragma: allowlist secret
  }
}

data "aws_secretsmanager_secret" "django_secret" {
  arn = aws_secretsmanager_secret.django_secret.arn
}

data "aws_secretsmanager_secret_version" "django_secret" {
  secret_id = data.aws_secretsmanager_secret.django_secret.id
}

resource "aws_secretsmanager_secret" "debug" {
  name        = "${var.prefix}-${var.project_name}-${var.env}-debug"
  description = "Django debug value for ${var.project_name}"
  tags = {
    SecretPurpose = "general" # pragma: allowlist secret
  }
}
data "aws_secretsmanager_secret" "debug" {
  arn = aws_secretsmanager_secret.debug.arn
}


data "aws_secretsmanager_secret_version" "debug" {
  secret_id = data.aws_secretsmanager_secret.debug.id
}

data "aws_secretsmanager_secret" "env_vars" {
  name = "${var.prefix}-${var.project_name}-${var.env}-environement-variables"
}

data "aws_secretsmanager_secret_version" "env_vars" {
  secret_id = data.aws_secretsmanager_secret.env_vars.id
}
