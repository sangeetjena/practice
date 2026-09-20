variable "project" { type = string }
variable "prefix" { type = string }
variable "region" { type = string }
variable "config" { type = any }
variable "runtime_accounts" { type = map(string) }
variable "flink" { type = any }

resource "google_compute_network" "network" {
  project                 = var.project
  name                    = var.prefix
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  project                  = var.project
  name                     = "${var.prefix}-workers"
  region                   = var.region
  ip_cidr_range            = var.config.subnet_cidr
  network                  = google_compute_network.network.id
  private_ip_google_access = true
  dynamic "secondary_ip_range" {
    for_each = var.flink.enabled ? { flink-pods = var.flink.pod_cidr, flink-services = var.flink.service_cidr } : {}
    content {
      range_name    = secondary_ip_range.key
      ip_cidr_range = secondary_ip_range.value
    }
  }
}

resource "google_compute_firewall" "workers" {
  project                 = var.project
  name                    = "${var.prefix}-internal-workers"
  network                 = google_compute_network.network.name
  source_ranges           = [var.config.subnet_cidr]
  target_service_accounts = values(var.runtime_accounts)
  allow { protocol = "tcp" }
  allow { protocol = "udp" }
  allow { protocol = "icmp" }
}

resource "google_compute_subnetwork_iam_member" "runtime" {
  for_each   = var.runtime_accounts
  project    = var.project
  region     = var.region
  subnetwork = google_compute_subnetwork.subnet.name
  role       = "roles/compute.networkUser"
  member     = "serviceAccount:${each.value}"
}

resource "google_compute_router" "router" {
  count   = var.config.enable_nat ? 1 : 0
  project = var.project
  name    = "${var.prefix}-nat"
  region  = var.region
  network = google_compute_network.network.id
}

resource "google_compute_router_nat" "nat" {
  count                              = var.config.enable_nat ? 1 : 0
  project                            = var.project
  name                               = "${var.prefix}-nat"
  region                             = var.region
  router                             = google_compute_router.router[0].name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
    name                    = google_compute_subnetwork.subnet.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}

output "subnetwork" { value = google_compute_subnetwork.subnet.self_link }
output "network" { value = google_compute_network.network.self_link }
