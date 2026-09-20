variable "project" { type = string }
variable "prefix" { type = string }
variable "region" { type = string }
variable "labels" { type = map(string) }
variable "accounts" { type = map(string) }
variable "deployer" { type = string }

resource "google_storage_bucket" "bucket" {
  for_each                    = toset(["raw", "curated", "staging", "artifacts", "control"])
  project                     = var.project
  name                        = "${var.project}-${var.prefix}-${each.key}"
  location                    = var.region
  labels                      = var.labels
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  versioning { enabled = true }
  dynamic "lifecycle_rule" {
    for_each = each.key == "staging" ? [1] : []
    content {
      condition { age = 7 }
      action { type = "Delete" }
    }
  }
}

locals {
  permissions = merge([
    for engine in ["dataflow", "dataproc"] : {
      "${engine}-raw"       = { account = engine, bucket = "raw", role = "roles/storage.objectViewer" }
      "${engine}-curated"   = { account = engine, bucket = "curated", role = "roles/storage.objectUser" }
      "${engine}-staging"   = { account = engine, bucket = "staging", role = "roles/storage.objectAdmin" }
      "${engine}-artifacts" = { account = engine, bucket = "artifacts", role = "roles/storage.objectViewer" }
    }
  ]...)
}

resource "google_storage_bucket_iam_member" "runtime" {
  for_each = local.permissions
  bucket   = google_storage_bucket.bucket[each.value.bucket].name
  role     = each.value.role
  member   = "serviceAccount:${var.accounts[each.value.account]}"
}

resource "google_storage_bucket_iam_member" "workflow_artifacts" {
  bucket = google_storage_bucket.bucket["artifacts"].name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.accounts.workflow}"
}

resource "google_storage_bucket_iam_member" "workflow_lock" {
  bucket = google_storage_bucket.bucket["control"].name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.accounts.workflow}"
}

resource "google_storage_bucket_iam_member" "publisher" {
  bucket = google_storage_bucket.bucket["artifacts"].name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.deployer}"
}

output "buckets" { value = { for key, bucket in google_storage_bucket.bucket : key => bucket.name } }
