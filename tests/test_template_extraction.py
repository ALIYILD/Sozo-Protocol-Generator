"""Tests for template extraction utilities."""
import pytest
from pathlib import Path


def test_slugify():
    """slugify converts text to lowercase underscore-separated slug."""
    from sozo_generator.core.utils import slugify

    assert slugify("Parkinson's Disease") == "parkinsons_disease"
    assert slugify("Hello World") == "hello_world"
    assert slugify("  Leading spaces  ") == "leading_spaces"
    assert slugify("Special!@#Chars") == "specialchars"


def test_content_hash():
    """content_hash produces deterministic MD5 hex digest."""
    from sozo_generator.core.utils import content_hash

    result1 = content_hash("hello world")
    result2 = content_hash("hello world")
    result3 = content_hash("different text")

    # Deterministic
    assert result1 == result2
    # Different inputs produce different hashes
    assert result1 != result3
    # Returns a 32-char hex string (MD5)
    assert isinstance(result1, str)
    assert len(result1) == 32


def test_ensure_dir(tmp_path):
    """ensure_dir creates a directory that does not yet exist."""
    from sozo_generator.core.utils import ensure_dir

    new_dir = tmp_path / "subdir" / "nested"
    assert not new_dir.exists()

    result = ensure_dir(new_dir)

    assert new_dir.exists()
    assert new_dir.is_dir()
    assert result == new_dir


def test_ensure_dir_existing(tmp_path):
    """ensure_dir on an existing directory does not raise."""
    from sozo_generator.core.utils import ensure_dir

    existing = tmp_path / "already_exists"
    existing.mkdir()

    result = ensure_dir(existing)
    assert result == existing


def test_truncate_text():
    """truncate_text cuts text at max_chars and appends ellipsis."""
    from sozo_generator.core.utils import truncate_text

    short = "Hello"
    assert truncate_text(short, max_chars=100) == short

    long_text = "word " * 200  # 1000 chars
    truncated = truncate_text(long_text, max_chars=50)
    assert len(truncated) <= 55  # max_chars + possible ellipsis
    assert truncated.endswith("\u2026")


def test_truncate_text_exact_boundary():
    """truncate_text does not truncate text that fits exactly."""
    from sozo_generator.core.utils import truncate_text

    text = "a" * 500
    result = truncate_text(text, max_chars=500)
    assert result == text
    assert not result.endswith("\u2026")
