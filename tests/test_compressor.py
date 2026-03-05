from unittest.mock import patch

import pytest

from shorthand_llm.compressor import ShorthandCompressor


@pytest.fixture
def compressor():
    return ShorthandCompressor()


# ── _mask_entities / _unmask_entities ──


class TestEntityMasking:
    def test_masks_url(self, compressor):
        text = "Visit https://example.com/page?q=1 for info."
        masked, replacements = compressor._mask_entities(text)
        assert "https://example.com/page?q=1" not in masked
        assert len(replacements) == 1
        token = list(replacements.keys())[0]
        assert token.startswith("__URL_")
        assert replacements[token] == "https://example.com/page?q=1"

    def test_masks_email(self, compressor):
        text = "Contact admin@example.com for help."
        masked, replacements = compressor._mask_entities(text)
        assert "admin@example.com" not in masked
        assert len(replacements) == 1
        token = list(replacements.keys())[0]
        assert token.startswith("__EMAIL_")

    def test_masks_multiple_entities(self, compressor):
        text = "Send to user@test.org or see http://test.org/docs"
        masked, replacements = compressor._mask_entities(text)
        assert "user@test.org" not in masked
        assert "http://test.org/docs" not in masked
        assert len(replacements) == 2

    def test_no_entities_returns_unchanged(self, compressor):
        text = "Plain text with no URLs or emails."
        masked, replacements = compressor._mask_entities(text)
        assert masked == text
        assert replacements == {}

    def test_unmask_restores_originals(self, compressor):
        text = "See https://example.com and mail user@test.com please."
        masked, replacements = compressor._mask_entities(text)
        restored = compressor._unmask_entities(masked, replacements)
        assert restored == text

    def test_roundtrip_preserves_text(self, compressor):
        text = "No entities here, just words."
        masked, replacements = compressor._mask_entities(text)
        restored = compressor._unmask_entities(masked, replacements)
        assert restored == text


# ── _find_safe_boundary ──


class TestFindSafeBoundary:
    def test_short_text_returns_full_length(self, compressor):
        text = "Short."
        assert compressor._find_safe_boundary(text, 100, 0) == len(text)

    def test_cuts_at_sentence_boundary(self, compressor):
        text = "First sentence. Second sentence. Third sentence. Overflow text here."
        boundary = compressor._find_safe_boundary(text, 50, 0)
        assert text[boundary - 2] == "."
        assert boundary <= 50

    def test_cuts_at_word_boundary_when_no_sentence(self, compressor):
        text = "word " * 20  # 100 chars, no sentence endings
        boundary = compressor._find_safe_boundary(text, 27, 0)
        assert text[boundary - 1] == " "

    def test_hard_limit_when_no_boundaries(self, compressor):
        text = "x" * 200
        boundary = compressor._find_safe_boundary(text, 50, 0)
        assert boundary == 50

    def test_respects_floor(self, compressor):
        text = "A. B. C. D. E. F. This is the target zone. End."
        boundary = compressor._find_safe_boundary(text, 48, 30)
        assert boundary >= 30
        assert boundary <= 48


# ── stream_compress ──


class TestStreamCompress:
    def test_short_input_yields_one_chunk(self, compressor):
        with patch.object(compressor, "_query_ollama", side_effect=lambda t: f"compressed({len(t)})"):
            results = list(compressor.stream_compress(["Hello world."], chunk_size=100, overlap_size=10))
        assert len(results) == 1
        assert results[0].startswith("compressed(")

    def test_long_input_yields_multiple_chunks(self, compressor):
        with patch.object(compressor, "_query_ollama", side_effect=lambda t: f"c({len(t)})"):
            lines = ["word " * 50 + "\n"] * 10  # ~2600 chars total
            results = list(compressor.stream_compress(lines, chunk_size=500, overlap_size=50))
        assert len(results) >= 2

    def test_empty_input_yields_nothing(self, compressor):
        with patch.object(compressor, "_query_ollama", side_effect=lambda t: "compressed"):
            results = list(compressor.stream_compress([], chunk_size=100, overlap_size=10))
        assert len(results) == 0

    def test_whitespace_only_input_yields_nothing(self, compressor):
        with patch.object(compressor, "_query_ollama", side_effect=lambda t: "compressed"):
            results = list(compressor.stream_compress(["   ", "\n", "  \t  "], chunk_size=100, overlap_size=10))
        assert len(results) == 0

    def test_exact_chunk_size_input(self, compressor):
        with patch.object(compressor, "_query_ollama", side_effect=lambda t: f"c({len(t)})"):
            text = "a" * 100
            results = list(compressor.stream_compress([text], chunk_size=100, overlap_size=10))
        assert len(results) >= 1
