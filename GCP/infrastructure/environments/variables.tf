variable "config" {
  description = "Validated, merged YAML emitted by gcp-platform render. Never put secret values here."
  type        = any
  validation {
    condition     = contains(["dev", "preprod", "prod"], var.config.environment)
    error_message = "Unknown deployment environment."
  }
}

variable "config_hash" {
  type = string
}

variable "release" {
  description = "Immutable artifact manifest. Null provisions infrastructure with schedules paused."
  type = object({
    version               = string
    dataflow_template_uri = string
    dataflow_image        = string
    dataproc_image        = string
    dataproc_main_uri     = string
    python_archive_uri    = string
  })
  default = null
}
