variable "project" { type = string }
variable "prefix" { type = string }
variable "region" { type = string }
variable "labels" { type = map(string) }
variable "accounts" { type = map(string) }

resource "google_bigquery_dataset" "analytics" {
  project                    = var.project
  dataset_id                 = replace(var.prefix, "-", "_")
  location                   = var.region
  labels                     = var.labels
  delete_contents_on_destroy = false
}

resource "google_bigquery_dataset_iam_member" "writer" {
  for_each   = toset(["dataflow", "dataproc"])
  project    = var.project
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.accounts[each.key]}"
}

resource "google_project_iam_member" "query" {
  for_each = toset(["dataflow", "dataproc"])
  project  = var.project
  role     = "roles/bigquery.jobUser"
  member   = "serviceAccount:${var.accounts[each.key]}"
}

output "dataset_id" { value = google_bigquery_dataset.analytics.dataset_id }
