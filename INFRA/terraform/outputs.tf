output "postgres_endpoint" {
  value       = "citus-coordinator.postgres.svc.cluster.local:5432"
  description = "Internal Citus coordinator endpoint."
}

output "cassandra_endpoint" {
  value       = "cassandra.cassandra.svc.cluster.local:9042"
  description = "Internal Cassandra CQL endpoint."
}

output "qdrant_endpoints" {
  value = {
    rest = "qdrant.qdrant.svc.cluster.local:6333"
    grpc = "qdrant.qdrant.svc.cluster.local:6334"
  }
  description = "Internal Qdrant REST and gRPC endpoints."
}

output "timescale_endpoint" {
  value       = "timescale.timescale.svc.cluster.local:5432"
  description = "Internal TimescaleDB endpoint for stock bars."
}

output "redis_endpoint" {
  value       = "redis.redis.svc.cluster.local:6379"
  description = "Internal Redis endpoint for ephemeral stock cache and queues."
}
