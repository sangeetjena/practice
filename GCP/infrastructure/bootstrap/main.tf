# Run once per existing, billing-enabled GCP project using an administrator identity.
# Bootstrap starts with local state; migrate it to the created bucket after first apply.
terraform {
  required_version = ">= 1.9, < 2.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" { project = var.project_id }

variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "asia-south1"
}
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "preprod", "prod"], var.environment)
    error_message = "Environment must be dev, preprod or prod."
  }
}
variable "github_repository" {
  description = "Exact owner/repository name"
  type        = string
}
variable "github_repository_id" {
  description = "GitHub's immutable numeric repository ID"
  type        = string
}
variable "github_owner_id" {
  description = "GitHub's immutable numeric owner ID"
  type        = string
}
variable "release_branch" {
  type    = string
  default = "master"
}

variable "enable_flink" {
  description = "Grant the trusted infrastructure deployer GKE administration when provisioning Flink."
  type        = bool
  default     = false
}

resource "google_project_iam_member" "gke_deployer" {
  count   = var.enable_flink ? 1 : 0
  project = var.project_id
  role    = "roles/container.admin"
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

resource "google_project_service" "api" {
  for_each = toset([
    "iam.googleapis.com", "iamcredentials.googleapis.com", "sts.googleapis.com",
    "cloudresourcemanager.googleapis.com", "storage.googleapis.com", "serviceusage.googleapis.com"
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "state" {
  project                     = var.project_id
  name                        = "${var.project_id}-terraform-state"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  versioning { enabled = true }
  lifecycle { prevent_destroy = true }
  depends_on = [google_project_service.api]
}

resource "google_service_account" "deployer" {
  project      = var.project_id
  account_id   = "gcp-deployer"
  display_name = "Protected CI infrastructure deployer (${var.environment})"
  depends_on   = [google_project_service.api]
}

resource "google_iam_workload_identity_pool" "github" {
  project                   = var.project_id
  workload_identity_pool_id = "github-deploy"
  display_name              = "GitHub protected environment"
  depends_on                = [google_project_service.api]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  attribute_mapping = {
    "google.subject"                = "assertion.sub"
    "attribute.repository_id"       = "assertion.repository_id"
    "attribute.repository_owner_id" = "assertion.repository_owner_id"
  }
  attribute_condition = "assertion.repository_id == '${var.github_repository_id}' && assertion.repository_owner_id == '${var.github_owner_id}' && assertion.ref == 'refs/heads/${var.release_branch}' && assertion.sub == 'repo:${var.github_repository}:environment:gcp-${var.environment}'"
  oidc { issuer_uri = "https://token.actions.githubusercontent.com" }
}

resource "google_service_account_iam_member" "federation" {
  service_account_id = google_service_account.deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.github_repository_id}"
}

# This is a privileged infrastructure identity. Limit who can edit or approve its workflow.
resource "google_project_iam_member" "deployer" {
  for_each = toset([
    "roles/serviceusage.serviceUsageAdmin", "roles/compute.networkAdmin", "roles/compute.securityAdmin",
    "roles/iam.serviceAccountAdmin", "roles/iam.roleAdmin", "roles/resourcemanager.projectIamAdmin",
    "roles/storage.admin", "roles/bigquery.admin", "roles/bigtable.admin",
    "roles/artifactregistry.admin", "roles/workflows.admin", "roles/cloudscheduler.admin",
    "roles/monitoring.editor"
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

resource "google_project_iam_custom_role" "secret_provisioner" {
  project = var.project_id
  role_id = "secretContainerProvisioner"
  title   = "Provision secret containers without reading values"
  permissions = [
    "secretmanager.secrets.create", "secretmanager.secrets.delete", "secretmanager.secrets.get",
    "secretmanager.secrets.getIamPolicy", "secretmanager.secrets.list",
    "secretmanager.secrets.setIamPolicy", "secretmanager.secrets.update"
  ]
}

resource "google_project_iam_member" "secret_provisioner" {
  project = var.project_id
  role    = google_project_iam_custom_role.secret_provisioner.name
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

output "workload_identity_provider" { value = google_iam_workload_identity_pool_provider.github.name }
output "deployment_service_account" { value = google_service_account.deployer.email }
output "state_bucket" { value = google_storage_bucket.state.name }
