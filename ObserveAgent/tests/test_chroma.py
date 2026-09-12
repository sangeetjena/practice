from observe_agent.knowledge import HashEmbedding
from observe_agent.vector_store import ChromaKnowledgeStore


def test_chroma_persists_filters_and_versions(tmp_path):
    store = ChromaKnowledgeStore(tmp_path / "audit.db", HashEmbedding(), tmp_path / "vectors")
    metadata = {"tenant_scope": "acme", "service": "orders", "review_status": "approved"}
    store.ingest("runbook", "# Resolution\nOld fix", metadata)
    store.ingest("runbook", "# Resolution\nNew pool fix", metadata)
    assert store.search("pool", tenant_id="globex", service="orders") == []
    hits = store.search("pool", tenant_id="acme", service="orders")
    assert len(hits) == 1
    assert "New pool" in hits[0].content
    reopened = ChromaKnowledgeStore(tmp_path / "audit.db", HashEmbedding(), tmp_path / "vectors")
    assert reopened.search("pool", tenant_id="acme", service="orders")
