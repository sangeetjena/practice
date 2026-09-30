variable "kubeconfig_path" {
  description = "Path to the kubeconfig for the already-created kind cluster."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Kubeconfig context for the already-created kind cluster."
  type        = string
  default     = "kind-local-platform"
}

variable "postgres_password" {
  description = "Local PostgreSQL/Citus superuser password, sourced from .env."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.postgres_password) >= 12
    error_message = "POSTGRES_PASSWORD must contain at least 12 characters."
  }
}

variable "cassandra_password" {
  description = "Local Cassandra user password, sourced from .env."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.cassandra_password) >= 12
    error_message = "CASSANDRA_PASSWORD must contain at least 12 characters."
  }
}

variable "qdrant_api_key" {
  description = "Local Qdrant API key, sourced from .env."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.qdrant_api_key) >= 16
    error_message = "QDRANT_API_KEY must contain at least 16 characters."
  }
}

variable "timescale_password" {
  description = "Local TimescaleDB superuser password, sourced from .env."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.timescale_password) >= 12
    error_message = "TIMESCALE_PASSWORD must contain at least 12 characters."
  }
}

variable "redis_password" {
  description = "Local Redis password, sourced from .env."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.redis_password) >= 12
    error_message = "REDIS_PASSWORD must contain at least 12 characters."
  }
}

variable "enable_monitoring" {
  description = "Install disposable local Prometheus/Grafana when explicitly enabled."
  type        = bool
  default     = false
}

variable "grafana_password" {
  description = "Local Grafana admin password; required only when monitoring is enabled."
  type        = string
  sensitive   = true
  default     = ""
}
