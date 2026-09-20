variable "project" { type = string }
variable "region" { type = string }
variable "secrets" { type = any }
variable "accounts" { type = map(string) }

# Containers and IAM only. Payloads must never enter Terraform state.
resource "google_secret_manager_secret" "secret" {
  for_each  = var.secrets
  project   = var.project
  secret_id = each.value.secret_id
  replication {
    user_managed {
      replicas { location = var.region }
    }
  }
}

locals {
  readers = flatten([
    for key, secret in var.secrets : [
      for reader in secret.readers : { key = key, reader = reader }
    ]
  ])
}

resource "google_secret_manager_secret_iam_member" "reader" {
  for_each  = { for item in local.readers : "${item.key}-${item.reader}" => item }
  project   = var.project
  secret_id = google_secret_manager_secret.secret[each.value.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.accounts[each.value.reader]}"
}

output "versions" {
  value = {
    for key, secret in var.secrets : key => "${google_secret_manager_secret.secret[key].id}/versions/${secret.version}"
  }
}
