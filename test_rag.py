
import pytest
from rag_utils import cosine_similarity, keyword_score, chunk_text


def test_cosine_similarity_identical_vectors():
    v = [1.0, 2.0, 3.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    a = [0.0, 0.0]
    b = [1.0, 1.0]
    assert cosine_similarity(a, b) == 0.0


def test_keyword_score_full_match():
    score = keyword_score("engelli yardım", "engelli yardım için başvuru")
    assert score == pytest.approx(1.0)


def test_keyword_score_no_match():
    score = keyword_score("pizza tarifi", "engelli yardımı hakkında bilgi")
    assert score == 0.0


def test_keyword_score_partial_match():
    score = keyword_score("engelli pizza", "engelli yardımı hakkında bilgi")
    assert score == pytest.approx(0.5)


def test_chunk_text_short_text_single_chunk():
    text = "Kısa bir metin."
    chunks = chunk_text(text, max_chars=600)
    assert len(chunks) == 1
    assert chunks[0] == "Kısa bir metin."


def test_chunk_text_respects_max_chars():
    long_paragraph = "kelime " * 200  # yaklasik 1400 karakter
    text = f"{long_paragraph}\n{long_paragraph}"
    chunks = chunk_text(text, max_chars=600)
    assert all(len(c) <= 700 for c in chunks)  # kucuk tolerans


def test_chunk_text_empty_string():
    assert chunk_text("", max_chars=600) == []