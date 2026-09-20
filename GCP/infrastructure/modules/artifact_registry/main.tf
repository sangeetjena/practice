variable "project" { type = string }
variable "prefix" { type = string }
variable "region" { type = string }
variable "accounts" { type = map(string) }
variable "deployer" { type = string }

resource "google_artifact_registry_repository" "images" {
  project       = var.project
  location      = var.region
  repository_id = var.prefix
  format        = "DOCKER"
  docker_config { immutable_tags = true }
}

resource "google_artifact_registry_repository_iam_member" "reader" {
  for_each   = toset(["dataflow", "dataproc"])
  project    = var.project
  location   = var.region
  repository = google_artifact_registry_repository.images.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${var.accounts[each.key]}"
}

resource "google_artifact_registry_repository_iam_member" "publisher" {
  project    = var.project
  location   = var.region
  repository = google_artifact_registry_repository.images.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${var.deployer}"
}

output "repository" {
  value = "${var.region}-docker.pkg.dev/${var.project}/${google_artifact_registry_repository.images.repository_id}"
}
