output "platform" {
  value = {
    project_id       = local.project
    region           = var.config.region
    environment      = var.config.environment
    config_hash      = var.config_hash
    buckets          = module.storage.buckets
    service_accounts = module.iam.accounts
    subnetwork       = module.networking.subnetwork
    repository       = module.artifact_registry.repository
    bigquery_dataset = module.bigquery.dataset_id
    secret_versions  = module.secret_manager.versions
    workflows        = { for name, workflow in google_workflows_workflow.job : name => workflow.name }
    release          = var.release
    flink            = var.config.flink.enabled ? module.gke[0].platform : null
  }
}
