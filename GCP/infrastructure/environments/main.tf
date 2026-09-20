locals {
  project = var.config.project_id
  prefix  = "${var.config.name}-${var.config.environment}"
  labels  = { environment = var.config.environment, platform = var.config.name, managed_by = "terraform" }
  apis = toset([
    "compute.googleapis.com", "iam.googleapis.com", "iamcredentials.googleapis.com",
    "storage.googleapis.com", "artifactregistry.googleapis.com", "dataflow.googleapis.com",
    "dataproc.googleapis.com", "bigquery.googleapis.com", "bigtable.googleapis.com",
    "bigtableadmin.googleapis.com", "secretmanager.googleapis.com", "workflows.googleapis.com",
    "workflowexecutions.googleapis.com", "cloudscheduler.googleapis.com",
    "logging.googleapis.com", "monitoring.googleapis.com", "container.googleapis.com"
  ])
}

resource "google_project_service" "api" {
  for_each           = local.apis
  project            = local.project
  service            = each.value
  disable_on_destroy = false
}

resource "google_project_service_identity" "agent" {
  provider   = google-beta
  for_each   = toset(["dataflow.googleapis.com", "dataproc.googleapis.com", "cloudscheduler.googleapis.com"])
  project    = local.project
  service    = each.value
  depends_on = [google_project_service.api]
}

resource "google_project_iam_member" "service_agent" {
  for_each = {
    "dataflow.googleapis.com"       = "roles/dataflow.serviceAgent"
    "dataproc.googleapis.com"       = "roles/dataproc.serviceAgent"
    "cloudscheduler.googleapis.com" = "roles/cloudscheduler.serviceAgent"
  }
  project = local.project
  role    = each.value
  member  = "serviceAccount:${google_project_service_identity.agent[each.key].email}"
}

module "iam" {
  source      = "../modules/iam"
  project     = local.project
  prefix      = local.prefix
  access      = var.config.access
  environment = var.config.environment
  depends_on  = [google_project_service.api]
}

module "networking" {
  source           = "../modules/networking"
  project          = local.project
  prefix           = local.prefix
  region           = var.config.region
  config           = var.config.network
  flink            = var.config.flink
  runtime_accounts = { dataflow = module.iam.accounts.dataflow, dataproc = module.iam.accounts.dataproc }
  depends_on       = [google_project_service.api]
}

module "storage" {
  source     = "../modules/storage"
  project    = local.project
  prefix     = local.prefix
  region     = var.config.region
  labels     = local.labels
  accounts   = module.iam.accounts
  deployer   = var.config.access.deployment_service_account
  depends_on = [google_project_service.api]
}

module "artifact_registry" {
  source     = "../modules/artifact_registry"
  project    = local.project
  prefix     = local.prefix
  region     = var.config.region
  accounts   = module.iam.accounts
  deployer   = var.config.access.deployment_service_account
  depends_on = [google_project_service.api]
}

module "bigquery" {
  source     = "../modules/bigquery"
  project    = local.project
  prefix     = local.prefix
  region     = var.config.region
  labels     = local.labels
  accounts   = module.iam.accounts
  depends_on = [google_project_service.api]
}

module "bigtable" {
  source     = "../modules/bigtable"
  count      = var.config.bigtable.enabled ? 1 : 0
  project    = local.project
  prefix     = local.prefix
  config     = var.config.bigtable
  labels     = local.labels
  account    = module.iam.accounts.dataflow
  depends_on = [google_project_service.api]
}

module "secret_manager" {
  source     = "../modules/secret_manager"
  project    = local.project
  region     = var.config.region
  secrets    = var.config.secrets
  accounts   = module.iam.accounts
  depends_on = [google_project_service.api]
}

module "gke" {
  source        = "../modules/gke"
  count         = var.config.flink.enabled ? 1 : 0
  project       = local.project
  region        = var.config.region
  prefix        = local.prefix
  config        = var.config.flink
  network       = module.networking.network
  subnetwork    = module.networking.subnetwork
  buckets       = module.storage.buckets
  repository_id = local.prefix
  deployer      = var.config.access.deployment_service_account
  depends_on    = [google_project_service.api, module.artifact_registry]
}
