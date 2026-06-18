from app.core.config import settings
from app.services.embedding import EmbeddingService


def test_mock_embedding_is_deterministic_and_configured_dimension():
    service = EmbeddingService()

    first = service.embed("portable grinder")
    second = service.embed("portable grinder")

    assert first == second
    assert len(first) == settings.embedding_dimensions
