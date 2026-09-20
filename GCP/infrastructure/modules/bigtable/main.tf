variable "project" { type = string }
variable "prefix" { type = string }
variable "config" { type = any }
variable "labels" { type = map(string) }
variable "account" { type = string }

resource "google_bigtable_instance" "instance" {
  project             = var.project
  name                = "${var.prefix}-bt"
  deletion_protection = true
  labels              = var.labels
  cluster {
    cluster_id   = "${var.prefix}-bt-1"
    zone         = var.config.zone
    storage_type = "SSD"
    autoscaling_config {
      min_nodes  = var.config.min_nodes
      max_nodes  = var.config.max_nodes
      cpu_target = var.config.cpu_target
    }
  }
}

resource "google_bigtable_table" "metrics" {
  project       = var.project
  instance_name = google_bigtable_instance.instance.name
  name          = var.config.table
  column_family { family = var.config.column_family }
}

resource "google_bigtable_app_profile" "batch" {
  project        = var.project
  instance       = google_bigtable_instance.instance.name
  app_profile_id = "batch"
  single_cluster_routing {
    cluster_id                 = "${var.prefix}-bt-1"
    allow_transactional_writes = true
  }
  ignore_warnings = true
}

resource "google_bigtable_instance_iam_member" "writer" {
  project  = var.project
  instance = google_bigtable_instance.instance.name
  role     = "roles/bigtable.user"
  member   = "serviceAccount:${var.account}"
}

output "instance" { value = google_bigtable_instance.instance.name }
output "app_profile" { value = google_bigtable_app_profile.batch.app_profile_id }
