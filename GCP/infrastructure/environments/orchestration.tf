locals {
  job_parameters = {
    for name, job in var.config.jobs : name => {
      use_case       = job.use_case
      input_uri      = "gs://${module.storage.buckets.raw}/${job.input_prefix}"
      output_uri     = "gs://${module.storage.buckets.curated}/${job.output_prefix}"
      target_project = local.project
      config_hash    = var.config_hash
      secret_version = job.secret != null ? module.secret_manager.versions[job.secret] : ""
      api_url        = job.api_url != null ? job.api_url : ""
      bt_instance    = var.config.bigtable.enabled ? module.bigtable[0].instance : ""
      bt_table       = var.config.bigtable.table
      bt_family      = var.config.bigtable.column_family
      bt_app_profile = var.config.bigtable.enabled ? module.bigtable[0].app_profile : ""
    }
  }
  # Exactly these Terraform-resolved resource references reach the launcher.
  specs = {
    for name, job in var.config.jobs : name => {
      engine          = job.engine
      job_key         = name
      project         = local.project
      region          = var.config.region
      control_bucket  = module.storage.buckets.control
      timeout_seconds = job.timeout_seconds
      release_ready   = var.release != null
      release_version = var.release != null ? var.release.version : "unpublished"
      parameters      = local.job_parameters[name]
      dataflow = {
        launchParameter = {
          containerSpecGcsPath = var.release != null ? var.release.dataflow_template_uri : ""
          parameters = merge(local.job_parameters[name], {
            sdk_container_image = var.release != null ? var.release.dataflow_image : ""
          })
          environment = {
            serviceAccountEmail = module.iam.accounts.dataflow
            subnetwork          = module.networking.subnetwork
            ipConfiguration     = "WORKER_IP_PRIVATE"
            tempLocation        = "gs://${module.storage.buckets.staging}/dataflow/temp"
            stagingLocation     = "gs://${module.storage.buckets.staging}/dataflow/staging"
            machineType         = var.config.dataflow.machine_type
            numWorkers          = var.config.dataflow.initial_workers
            maxWorkers          = var.config.dataflow.max_workers
            diskSizeGb          = var.config.dataflow.disk_size_gb
            additionalUserLabels = merge(local.labels, {
              config_hash = substr(var.config_hash, 0, 16)
              job         = name
            })
          }
        }
      }
      dataproc = {
        pysparkBatch = {
          mainPythonFileUri = var.release != null ? var.release.dataproc_main_uri : ""
          pythonFileUris    = var.release != null ? [var.release.python_archive_uri] : []
          args = flatten([
            for key, value in local.job_parameters[name] : ["--${key}", value] if value != ""
          ])
        }
        runtimeConfig = {
          version        = var.config.dataproc.runtime_version
          containerImage = var.release != null ? var.release.dataproc_image : ""
          properties = {
            "spark.executor.cores"                 = tostring(var.config.dataproc.executor_cores)
            "spark.executor.instances"             = tostring(var.config.dataproc.executor_instances)
            "spark.dynamicAllocation.enabled"      = "true"
            "spark.dynamicAllocation.minExecutors" = tostring(var.config.dataproc.executor_instances)
            "spark.dynamicAllocation.maxExecutors" = tostring(var.config.dataproc.max_executors)
          }
        }
        environmentConfig = {
          executionConfig = {
            serviceAccount = module.iam.accounts.dataproc
            subnetworkUri  = module.networking.subnetwork
            stagingBucket  = module.storage.buckets.staging
            ttl            = var.config.dataproc.ttl
          }
        }
        labels = merge(local.labels, { config_hash = substr(var.config_hash, 0, 16), job = name })
      }
    }
  }
}

resource "google_workflows_workflow" "job" {
  for_each        = var.config.jobs
  project         = local.project
  region          = var.config.region
  name            = "${local.prefix}-${each.key}"
  service_account = module.iam.accounts.workflow
  description     = "${each.value.engine} ${each.value.use_case}; configuration ${var.config_hash}"
  source_contents = file("${path.module}/../../orchestration/batch.yaml")
  user_env_vars   = { WORKLOAD_SPEC = jsonencode(local.specs[each.key]) }
  call_log_level  = "LOG_ERRORS_ONLY"
  labels          = local.labels
  depends_on      = [google_project_service.api, google_project_iam_member.service_agent]
}

resource "google_project_iam_member" "scheduler" {
  project = local.project
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${module.iam.accounts.scheduler}"
}

locals {
  # Developers may execute in dev only. Operators can execute in their configured environment.
  operators = toset(concat(
    var.config.access.operator_groups,
    var.config.environment == "dev" ? var.config.access.developer_groups : []
  ))
}

resource "google_project_iam_member" "operator" {
  for_each = local.operators
  project  = local.project
  role     = "roles/workflows.invoker"
  member   = "group:${each.value}"
}

resource "google_cloud_scheduler_job" "batch" {
  for_each         = { for name, job in var.config.jobs : name => job if job.schedule.enabled }
  project          = local.project
  region           = var.config.region
  name             = "${local.prefix}-${each.key}"
  schedule         = each.value.schedule.cron
  time_zone        = each.value.schedule.timezone
  paused           = var.release == null
  attempt_deadline = "60s"
  retry_config {
    retry_count = 0
  }
  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.job[each.key].id}/executions"
    headers     = { "Content-Type" = "application/json" }
    body        = base64encode(jsonencode({ argument = jsonencode({ scheduled = true }) }))
    oauth_token {
      service_account_email = module.iam.accounts.scheduler
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
  depends_on = [google_project_iam_member.scheduler]
}

# Scheduler only observes acceptance by Workflows. This policy observes actual execution failure.
resource "google_monitoring_alert_policy" "workflow_failure" {
  project      = local.project
  display_name = "${local.prefix}: batch workflow failures"
  combiner     = "OR"
  conditions {
    display_name = "Failed batch workflow execution"
    condition_threshold {
      filter          = "resource.type = \"workflows.googleapis.com/Workflow\" AND metric.type = \"workflows.googleapis.com/finished_execution_count\" AND metric.labels.status = \"FAILED\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }
  documentation {
    content   = "Inspect the failed Workflows execution and its Dataflow job or Dataproc batch. See docs/operations.md. Add notification channels before relying on this policy for paging."
    mime_type = "text/markdown"
  }
  depends_on = [google_project_service.api]
}
