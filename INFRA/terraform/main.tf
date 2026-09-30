resource "helm_release" "cassandra" {
  name             = "cassandra"
  namespace        = "cassandra"
  chart            = "${path.module}/../helm/cassandra"
  create_namespace = false
  wait             = true
  timeout          = 1800
  cleanup_on_fail  = true

  values = [file("${path.module}/../helm/cassandra/values.yaml"), yamlencode({ dbUser = { password = var.cassandra_password } })]

}

resource "helm_release" "qdrant" {
  name             = "qdrant"
  namespace        = "qdrant"
  repository       = "https://qdrant.github.io/qdrant-helm"
  chart            = "qdrant"
  version          = "1.19.1"
  create_namespace = false
  wait             = true
  timeout          = 900
  cleanup_on_fail  = true

  values = [file("${path.module}/../helm/qdrant/values.yaml"), yamlencode({ apiKey = var.qdrant_api_key })]

}

resource "helm_release" "citus" {
  name             = "citus"
  namespace        = "postgres"
  chart            = "${path.module}/../helm/citus"
  create_namespace = false
  wait             = true
  timeout          = 1200
  cleanup_on_fail  = true

  values = [file("${path.module}/../helm/citus/values.yaml"), yamlencode({ postgres = { password = var.postgres_password } })]

}

resource "helm_release" "timescale" {
  name             = "timescale"
  namespace        = "timescale"
  chart            = "${path.module}/../helm/timescale"
  create_namespace = false
  wait             = true
  timeout          = 900
  cleanup_on_fail  = true

  values = [file("${path.module}/../helm/timescale/values.yaml"), yamlencode({ postgres = { password = var.timescale_password } })]
}

resource "helm_release" "redis" {
  name             = "redis"
  namespace        = "redis"
  chart            = "${path.module}/../helm/redis"
  create_namespace = false
  wait             = true
  timeout          = 900
  cleanup_on_fail  = true

  values = [file("${path.module}/../helm/redis/values.yaml"), yamlencode({ password = var.redis_password })]
}

resource "helm_release" "monitoring" {
  count      = var.enable_monitoring ? 1 : 0
  name       = "monitoring"
  namespace  = "monitoring"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = "69.8.2"
  wait       = true
  timeout    = 900

  values = [file("${path.module}/../helm/monitoring/values.yaml"), yamlencode({
    grafana = { adminPassword = var.grafana_password }
    prometheus = { prometheusSpec = { additionalScrapeConfigs = [{
      job_name       = "qdrant"
      authorization  = { type = "Bearer", credentials = var.qdrant_api_key }
      static_configs = [{ targets = [for i in range(3) : "qdrant-${i}.qdrant-headless.qdrant.svc.cluster.local:6333"] }]
    }] } }
  })]
  lifecycle {
    precondition {
      condition     = length(var.grafana_password) >= 12
      error_message = "Set GRAFANA_PASSWORD to at least 12 characters when enabling monitoring."
    }
  }
}
