output "postgres_endpoint" {
  value       = var.enable_citus ? "citus-coordinator.postgres.svc.cluster.local:5432" : null
  description = "Internal Citus coordinator endpoint."
}

output "cassandra_endpoint" {
  value       = var.enable_cassandra ? "cassandra.cassandra.svc.cluster.local:9042" : null
  description = "Internal Cassandra CQL endpoint."
}

output "qdrant_endpoints" {
  value = var.enable_qdrant ? {
    rest = "qdrant.qdrant.svc.cluster.local:6333"
    grpc = "qdrant.qdrant.svc.cluster.local:6334"
  } : null
  description = "Internal Qdrant REST and gRPC endpoints."
}

output "timescale_endpoint" {
  value       = var.enable_timescale ? "timescale.timescale.svc.cluster.local:5432" : null
  description = "Internal TimescaleDB endpoint for stock bars."
}

output "redis_endpoint" {
  value       = var.enable_redis ? "redis.redis.svc.cluster.local:6379" : null
  description = "Internal Redis endpoint for ephemeral stock cache and queues."
}
