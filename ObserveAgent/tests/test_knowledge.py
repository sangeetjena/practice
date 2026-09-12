from observe_agent.knowledge import HashEmbedding, MarkdownChunker, SQLiteKnowledgeStore


def test_markdown_chunker_preserves_semantic_section():
    text = "# Symptom\nLatency increased.\n\n# Resolution\nRollback the bad release."

    chunks = MarkdownChunker(max_chars=200).split(text)

    assert [metadata["section"] for _, metadata in chunks] == ["Symptom", "Resolution"]
    assert chunks[1][0].startswith("# Resolution")


def test_hybrid_search_filters_tenant_service_and_review_status(tmp_path):
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.db")
    approved = {
        "source_type": "incident_resolution",
        "review_status": "approved",
        "tenant_scope": "acme",
        "service": "orders",
    }
    store.ingest("acme-resolution", "# Resolution\nIncrease the orders connection pool.", approved)
    store.ingest(
        "globex-resolution",
        "# Resolution\nRollback the orders deployment.",
        {**approved, "tenant_scope": "globex"},
    )
    store.ingest(
        "draft-resolution",
        "# Resolution\nRestart everything.",
        {**approved, "review_status": "draft"},
    )

    hits = store.search("orders connection pool", tenant_id="acme", service="orders")

    assert [hit.source_id for hit in hits] == ["acme-resolution"]


def test_new_source_version_deactivates_old_chunks(tmp_path):
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.db")
    metadata = {
        "source_type": "runbook",
        "review_status": "approved",
        "tenant_scope": "global",
        "service": "orders",
    }
    store.ingest("orders-runbook", "# Resolution\nUse the old procedure.", metadata)
    store.ingest("orders-runbook", "# Resolution\nUse the reviewed new procedure.", metadata)

    hits = store.search("reviewed new procedure", tenant_id="acme", service="orders")

    assert len(hits) == 1
    assert "new procedure" in hits[0].content


def test_embedding_profile_change_requires_explicit_reindex(tmp_path):
    path = tmp_path / "knowledge.db"
    metadata = {
        "source_type": "runbook",
        "review_status": "approved",
        "tenant_scope": "global",
        "service": "orders",
    }
    SQLiteKnowledgeStore(path, HashEmbedding(64)).ingest(
        "runbook", "# Resolution\nIncrease the connection pool.", metadata
    )
    changed = SQLiteKnowledgeStore(path, HashEmbedding(96))

    assert changed.search("connection pool", tenant_id="acme", service="orders") == []
    assert changed.reindex() == 1
    assert changed.search("connection pool", tenant_id="acme", service="orders")
