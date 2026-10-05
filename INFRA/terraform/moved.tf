# Keep existing Helm releases in state when adding optional deployment flags.
moved {
  from = helm_release.citus
  to   = helm_release.citus[0]
}

moved {
  from = helm_release.cassandra
  to   = helm_release.cassandra[0]
}

moved {
  from = helm_release.qdrant
  to   = helm_release.qdrant[0]
}

moved {
  from = helm_release.timescale
  to   = helm_release.timescale[0]
}

moved {
  from = helm_release.redis
  to   = helm_release.redis[0]
}
