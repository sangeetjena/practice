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