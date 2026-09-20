variable "project" { type = string }
variable "region" { type = string }
variable "prefix" { type = string }
variable "config" { type = any }
variable "network" { type = string }
variable "subnetwork" { type = string }
variable "buckets" { type = map(string) }
variable "repository_id" { type = string }
variable "deployer" { type = string }

resource "google_service_account" "node" {
  project    = var.project
  account_id = "${var.prefix}-gke-node"
}

resource "google_project_iam_member" "node" {
  for_each = toset(["roles/container.defaultNodeServiceAccount"])
  project  = var.project
  role     = each.value
  member   = "serviceAccount:${google_service_account.node.email}"
}

resource "google_service_account_iam_member" "deployer_node" {
  service_account_id = google_service_account.node.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.deployer}"
}

resource "google_artifact_registry_repository_iam_member" "node" {
  project    = var.project
  location   = var.region
  repository = var.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.node.email}"
}

resource "google_service_account" "flink" {
  project    = var.project
  account_id = "${var.prefix}-flink"
}

resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.flink.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[${var.config.namespace}/flink-job]"
  depends_on         = [google_container_cluster.flink]
}

resource "google_storage_bucket" "state" {
  project                     = var.project
  name                        = "${var.project}-${var.prefix}-flink"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  # Never attach a time-based lifecycle rule: incremental checkpoints share SST files.
  versioning { enabled = true }
  lifecycle { prevent_destroy = true }
}

resource "google_storage_bucket_iam_member" "state" {
  bucket = google_storage_bucket.state.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.flink.email}"
}

resource "google_storage_bucket_iam_member" "raw" {
  bucket = var.buckets.raw
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.flink.email}"
}

resource "google_storage_bucket_iam_member" "curated" {
  bucket = var.buckets.curated
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${google_service_account.flink.email}"
}

resource "google_container_cluster" "flink" {
  project                  = var.project
  name                     = "${var.prefix}-flink"
  location                 = var.region
  network                  = var.network
  subnetwork               = var.subnetwork
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = true
  node_config {
    service_account = google_service_account.node.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }
  release_channel { channel = "REGULAR" }
  workload_identity_config { workload_pool = "${var.project}.svc.id.goog" }
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.config.master_cidr
  }
  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = toset(var.config.authorized_cidrs)
      content {
        cidr_block   = cidr_blocks.value
        display_name = "approved-runner"
      }
    }
  }
  ip_allocation_policy {
    cluster_secondary_range_name  = "flink-pods"
    services_secondary_range_name = "flink-services"
  }
  logging_config { enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"] }
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus { enabled = true }
  }
  depends_on = [google_project_iam_member.node, google_service_account_iam_member.deployer_node]
}

resource "google_container_node_pool" "workers" {
  project            = var.project
  name               = "flink-workers"
  location           = var.region
  cluster            = google_container_cluster.flink.name
  initial_node_count = 1
  autoscaling {
    total_min_node_count = var.config.min_nodes
    total_max_node_count = var.config.max_nodes
    location_policy      = "BALANCED"
  }
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  node_config {
    machine_type    = var.config.node_machine_type
    service_account = google_service_account.node.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    disk_size_gb    = 100
    disk_type       = "pd-balanced"
    metadata        = { disable-legacy-endpoints = "true" }
    workload_metadata_config { mode = "GKE_METADATA" }
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }
  depends_on = [google_project_iam_member.node, google_artifact_registry_repository_iam_member.node]
}

output "platform" {
  value = {
    cluster         = google_container_cluster.flink.name
    region          = var.region
    namespace       = var.config.namespace
    service_account = google_service_account.flink.email
    state_bucket    = google_storage_bucket.state.name
    rest_endpoint   = "http://orders-payments-rest.${var.config.namespace}.svc.cluster.local:8081"
  }
}
