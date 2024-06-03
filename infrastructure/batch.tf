
locals {
  batch_image_ecr_url = var.ecr_repository_uri
}

module "batch_compute" {
  source          = "../../i-ai-core-infrastructure/modules/batch/batch_compute_environment"
  account_id      = var.account_id
  project         = "i-dot-ai"
  name            = "consultations"
  region          = var.region
  vpc_id          = data.terraform_remote_state.vpc.outputs.vpc_id
  desired_vcpus   = 0
  min_vcpus       = 0
  max_vcpus       = 20
  private_subnets = data.terraform_remote_state.vpc.outputs.private_subnets
  state_bucket    = var.state_bucket
  instance_type   = "g5.xlarge"
  ecs_instance_role = aws_iam_role.ecsInstanceRole.name
}

module "batch_job_definition" {
  source                  = "../../i-ai-core-infrastructure/modules/batch/batch_job_definitons"
  account_id              = var.account_id
  project                 = "i-dot-ai"
  name                    = "consultations"
  region                  = var.region
  compute_environment_arn = [module.batch_compute.ec2_compute_environment_arn]
  state_bucket            = var.state_bucket
  image                   = "${local.batch_image_ecr_url}:${var.image_tag}"
  fargate_flag            = false
  env_vars                = local.batch_env_vars
}
