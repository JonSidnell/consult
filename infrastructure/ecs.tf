locals {
  rds_fqdn        = "${module.rds.rds_instance_username}:${module.rds.rds_instance_db_password}@${module.rds.db_instance_address}/${module.rds.db_instance_name}"
  secret_env_vars = jsondecode(data.aws_secretsmanager_secret_version.env_vars.secret_string)
  batch_env_vars = {
    "ENVIRONMENT"                          = terraform.workspace,
    "DJANGO_SECRET_KEY"                    = data.aws_secretsmanager_secret_version.django_secret.secret_string,
    "DEBUG"                                = local.secret_env_vars.DEBUG,
    "SAGEMAKER_ENDPOINT_NAME"              = local.secret_env_vars.SAGEMAKER_ENDPOINT_NAME
    "GOVUK_NOTIFY_API_KEY"                 = local.secret_env_vars.GOVUK_NOTIFY_API_KEY,
    "GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID" = local.secret_env_vars.GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID,
    "USE_SAGEMAKER_LLM"                    = local.secret_env_vars.USE_SAGEMAKER_LLM,
    "SENTRY_DSN"                           = local.secret_env_vars.SENTRY_DSN,
    "AWS_REGION"                           = local.secret_env_vars.AWS_REGION,
    "DATABASE_URL"                         = local.rds_fqdn,
    "DOMAIN_NAME"                          = "${local.host}",
    "RELEASE_HASH"                         = substr(var.image_tag, 0, 6)
  }


  esc_env_vars = merge({
    "BATCH_JOB_QUEUE"      = module.batch_job_definition.job_queue_name,
    "BATCH_JOB_DEFINITION" = module.batch_job_definition.job_definition_name,
  }, local.batch_env_vars)
}

module "ecs" {
  source             = "../../i-ai-core-infrastructure//modules/ecs"
  name               = local.name
  image_tag          = var.image_tag
  ecr_repository_uri = var.ecr_repository_uri
  ecs_cluster_id     = data.terraform_remote_state.platform.outputs.ecs_cluster_id
  ecs_cluster_name   = data.terraform_remote_state.platform.outputs.ecs_cluster_name
  health_check = {
    healthy_threshold   = 3
    unhealthy_threshold = 3
    accepted_response   = "200"
    path                = "/"
    timeout             = 6
    port                = 8000
  }
  environment_variables = local.esc_env_vars

  state_bucket                 = var.state_bucket
  vpc_id                       = data.terraform_remote_state.vpc.outputs.vpc_id
  private_subnets              = data.terraform_remote_state.vpc.outputs.private_subnets
  container_port               = "8000"
  load_balancer_security_group = module.load_balancer.load_balancer_security_group_id
  aws_lb_arn                   = module.load_balancer.alb_arn
  host                         = local.host
  route53_record_name          = aws_route53_record.type_a_record.name
  ip_whitelist                 = var.external_ips
  create_listener              = true
  task_additional_iam_policy   = aws_iam_policy.ecs.arn
  additional_execution_role_tags = {
    "RolePassableByRunner" = "True"
  }
}

resource "aws_route53_record" "type_a_record" {
  zone_id = var.hosted_zone_id
  name    = local.host
  type    = "A"

  alias {
    name                   = module.load_balancer.load_balancer_dns_name
    zone_id                = module.load_balancer.load_balancer_zone_id
    evaluate_target_health = true
  }
}


resource "aws_iam_policy" "ecs" {
  name        = "${local.name}-ecs-additional-policy"
  description = "Additional permissions for consultations ECS task"
  policy      = data.aws_iam_policy_document.ecs.json
  tags = {
    Environment = terraform.workspace
    Deployed    = "github"
  }
}

data "aws_iam_policy_document" "ecs" {
  # checkov:skip=CKV_AWS_109:KMS policies can't be restricted
  # checkov:skip=CKV_AWS_111:KMS policies can't be restricted

  statement {
    effect = "Allow"
    actions = [
      "batch:DescribeJobQueues",
      "batch:SubmitJob"
    ]
    resources = [
      "*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "sagemaker:CreateEndpoint",
    ]
    resources = [
      "*"
    ]
  }
}
