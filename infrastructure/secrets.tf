
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


resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.prefix}-${var.project_name}-${var.env}-app-secrets"
  description = "Django app secrets for ${var.project_name}"
  tags = {
    SecretPurpose = "general" # pragma: allowlist secret
  }
}

data "aws_secretsmanager_secret" "app_secrets" {
  arn = aws_secretsmanager_secret.app_secrets.arn
}

data "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = data.aws_secretsmanager_secret.app_secrets.id
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

resource "aws_secretsmanager_secret" "env_vars" {
  name        = "${var.prefix}-${var.project_name}-${var.env}-environement-variables"
  description = "Environment variables for ${var.project_name} in ${var.env} ECS. These are non-sensitive variables."
  tags = {
    SecretPurpose = "general"
  }
}

data "aws_secretsmanager_secret" "env_vars" {
  arn = aws_secretsmanager_secret.env_vars.arn
}

data "aws_secretsmanager_secret_version" "env_vars" {
  secret_id = data.aws_secretsmanager_secret.env_vars.id
}
