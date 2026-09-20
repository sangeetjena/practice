mock_provider "google" {}
mock_provider "google-beta" {}

run "dev_infrastructure" {
  command = plan
  variables {
    config      = jsondecode(file("../../build/dev/platform.tfvars.json")).config
    config_hash = jsondecode(file("../../build/dev/platform.tfvars.json")).config_hash
  }
  assert {
    condition     = length(google_cloud_scheduler_job.batch) == 0
    error_message = "Dev must not schedule jobs by default."
  }
  assert {
    condition     = local.specs["clean-orders"].dataflow.launchParameter.environment.maxWorkers == 3
    error_message = "Dev worker sizing did not reach the actual launch request."
  }
  assert {
    condition     = local.specs["daily-sales"].dataproc.runtimeConfig.properties["spark.dynamicAllocation.maxExecutors"] == "4"
    error_message = "Dev Spark sizing did not reach the actual launch request."
  }
}

run "prod_infrastructure" {
  command = plan
  variables {
    config      = jsondecode(file("../../build/prod/platform.tfvars.json")).config
    config_hash = jsondecode(file("../../build/prod/platform.tfvars.json")).config_hash
  }
  assert {
    condition     = google_cloud_scheduler_job.batch["clean-orders"].paused
    error_message = "Schedules must remain paused until a release exists."
  }
  assert {
    condition     = local.specs["clean-orders"].dataflow.launchParameter.environment.maxWorkers == 10
    error_message = "Prod worker sizing did not reach the actual launch request."
  }
  assert {
    condition     = local.specs["clean-orders"].dataflow.launchParameter.environment.ipConfiguration == "WORKER_IP_PRIVATE"
    error_message = "Worker public IPs must stay disabled."
  }
}

run "optional_flink_and_bigtable" {
  command = plan
  variables {
    config = merge(jsondecode(file("../../build/dev/platform.tfvars.json")).config, {
      network = { subnet_cidr = "10.40.0.0/20", enable_nat = true }
      flink = merge(jsondecode(file("../../build/dev/platform.tfvars.json")).config.flink, {
        enabled = true, authorized_cidrs = ["203.0.113.10/32"]
      })
      bigtable = merge(jsondecode(file("../../build/dev/platform.tfvars.json")).config.bigtable, { enabled = true })
    })
    config_hash = "test-config"
  }
  assert {
    condition     = length(module.gke) == 1 && length(module.bigtable) == 1
    error_message = "Optional infrastructure must follow configuration flags."
  }
  assert {
    condition     = module.gke[0].platform.rest_endpoint == "http://orders-payments-rest.flink.svc.cluster.local:8081"
    error_message = "JobManager must have the expected internal endpoint."
  }
}
