variable "project" { type = string }
variable "prefix" { type = string }
variable "environment" { type = string }
variable "access" { type = any }

resource "google_service_account" "account" {
  for_each     = toset(["dataflow", "dataproc", "workflow", "scheduler"])
  project      = var.project
  account_id   = "${var.prefix}-${each.key}"
  display_name = "${var.prefix}: ${each.key}"
}

locals {
  roles = {
    df_worker  = { account = "dataflow", role = "roles/dataflow.worker" }
    df_logs    = { account = "dataflow", role = "roles/logging.logWriter" }
    df_metrics = { account = "dataflow", role = "roles/monitoring.metricWriter" }
    df_usage   = { account = "dataflow", role = "roles/serviceusage.serviceUsageConsumer" }
    dp_worker  = { account = "dataproc", role = "roles/dataproc.worker" }
    dp_usage   = { account = "dataproc", role = "roles/serviceusage.serviceUsageConsumer" }
    wf_logs    = { account = "workflow", role = "roles/logging.logWriter" }
    wf_usage   = { account = "workflow", role = "roles/serviceusage.serviceUsageConsumer" }
  }
}

resource "google_project_iam_member" "runtime" {
  for_each = local.roles
  project  = var.project
  role     = each.value.role
  member   = "serviceAccount:${google_service_account.account[each.value.account].email}"
}

resource "google_project_iam_custom_role" "launcher" {
  project = var.project
  role_id = "${replace(var.prefix, "-", "_")}_launcher"
  title   = "Data platform batch launcher"
  permissions = [
    "dataflow.jobs.create", "dataflow.jobs.get", "dataflow.jobs.list", "dataflow.jobs.update",
    "dataproc.batches.create", "dataproc.batches.get", "dataproc.batches.list",
    "dataproc.operations.get", "dataproc.operations.cancel"
  ]
}

resource "google_project_iam_member" "launcher" {
  project = var.project
  role    = google_project_iam_custom_role.launcher.name
  member  = "serviceAccount:${google_service_account.account["workflow"].email}"
}

resource "google_service_account_iam_member" "workflow_runtime" {
  for_each           = toset(["dataflow", "dataproc"])
  service_account_id = google_service_account.account[each.key].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.account["workflow"].email}"
}

# The deployer can attach these identities to resources but cannot mint runtime tokens.
resource "google_service_account_iam_member" "deployer" {
  for_each           = google_service_account.account
  service_account_id = each.value.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.access.deployment_service_account}"
}

locals {
  viewers = toset(concat(var.access.viewer_groups, var.access.operator_groups, var.access.developer_groups))
  view_roles = toset([
    "roles/dataflow.viewer", "roles/dataproc.viewer", "roles/workflows.viewer", "roles/logging.viewer"
  ])
  view_bindings = {
    for pair in setproduct(local.viewers, local.view_roles) : "${pair[0]}:${pair[1]}" => pair
  }
}

resource "google_project_iam_member" "viewer" {
  for_each = local.view_bindings
  project  = var.project
  role     = each.value[1]
  member   = "group:${each.value[0]}"
}

output "accounts" {
  value = { for key, value in google_service_account.account : key => value.email }
}
