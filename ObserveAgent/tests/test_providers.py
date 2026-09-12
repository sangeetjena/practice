from types import SimpleNamespace

from observe_agent.knowledge import OpenAIEmbedding
from observe_agent.models import Hypothesis
from observe_agent.reasoner import ModelAnalysis, OpenAIReasoner


class FakeEmbeddings:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])])


def test_openai_embedding_uses_configured_model_and_dimensions():
    embeddings = FakeEmbeddings()
    client = SimpleNamespace(embeddings=embeddings)
    provider = OpenAIEmbedding("custom-embedding", "secret", dimensions=256, client=client)

    assert provider.embed("latency") == [0.1, 0.2]
    assert embeddings.kwargs == {
        "model": "custom-embedding",
        "input": "latency",
        "dimensions": 256,
    }


def test_openai_reasoner_filters_model_invented_citations():
    parsed = ModelAnalysis(
        summary="A dependency is slow.",
        known_facts=["p95 increased"],
        hypotheses=[Hypothesis(cause="dependency", confidence=0.8, supporting_evidence=["p95"])],
        recommended_actions=["inspect trace"],
        unknowns=[],
        citations=["invented#citation"],
    )
    responses = SimpleNamespace(parse=lambda **kwargs: SimpleNamespace(output_parsed=parsed))
    reasoner = OpenAIReasoner("model-a", "secret", client=SimpleNamespace(responses=responses))

    class Dumpable:
        id = "inc-1"
        tenant_id = "acme"
        service = "orders"

        def model_dump(self, **kwargs):
            return {}

    report = reasoner.analyze(Dumpable(), Dumpable(), [])

    assert report.citations == []
