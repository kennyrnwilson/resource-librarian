"""Tests for hashing utility functions."""

from pathlib import Path

import pytest

from resourcelibrarian.utils.hash import compute_file_hash, compute_text_hash, short_hash


# ========================================
# Text Hash Tests
# ========================================


def test_compute_text_hash_basic():
    """Test basic text hashing."""
    text = "Hello, World!"
    hash_result = compute_text_hash(text)

    assert hash_result.startswith("sha256_")
    assert len(hash_result) == 71  # 'sha256_' (7) + 64 hex chars


def test_compute_text_hash_consistent():
    """Test that same text produces same hash."""
    text = "Consistent hashing test"

    hash1 = compute_text_hash(text)
    hash2 = compute_text_hash(text)

    assert hash1 == hash2


def test_compute_text_hash_different_text():
    """Test that different texts produce different hashes."""
    text1 = "First text"
    text2 = "Second text"

    hash1 = compute_text_hash(text1)
    hash2 = compute_text_hash(text2)

    assert hash1 != hash2


def test_compute_text_hash_with_unicode():
    """Test hashing text with Unicode characters."""
    text = "Hello 世界 🌍"
    hash_result = compute_text_hash(text)

    assert hash_result.startswith("sha256_")
    assert len(hash_result) == 71


def test_compute_text_hash_empty_string():
    """Test hashing an empty string."""
    hash_result = compute_text_hash("")

    assert hash_result.startswith("sha256_")
    # SHA256 of empty string is well-known
    expected = "sha256_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert hash_result == expected


def test_compute_text_hash_multiline():
    """Test hashing multiline text."""
    text = """Line 1
Line 2
Line 3"""
    hash_result = compute_text_hash(text)

    assert hash_result.startswith("sha256_")
    assert len(hash_result) == 71


def test_compute_text_hash_with_md5():
    """Test hashing with MD5 algorithm."""
    text = "MD5 test"
    hash_result = compute_text_hash(text, algorithm="md5")

    assert hash_result.startswith("md5_")
    assert len(hash_result) == 36  # 'md5_' (4) + 32 hex chars


# ========================================
# File Hash Tests
# ========================================


def test_compute_file_hash_basic(tmp_path):
    """Test basic file hashing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("File content for hashing")

    hash_result = compute_file_hash(test_file)

    assert hash_result.startswith("sha256_")
    assert len(hash_result) == 71


def test_compute_file_hash_consistent(tmp_path):
    """Test that same file produces same hash."""
    test_file = tmp_path / "consistent.txt"
    test_file.write_text("Consistent file content")

    hash1 = compute_file_hash(test_file)
    hash2 = compute_file_hash(test_file)

    assert hash1 == hash2


def test_compute_file_hash_different_files(tmp_path):
    """Test that different files produce different hashes."""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text("Content A")
    file2.write_text("Content B")

    hash1 = compute_file_hash(file1)
    hash2 = compute_file_hash(file2)

    assert hash1 != hash2


def test_compute_file_hash_binary_file(tmp_path):
    """Test hashing a binary file."""
    binary_file = tmp_path / "binary.dat"
    binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd")

    hash_result = compute_file_hash(binary_file)

    assert hash_result.startswith("sha256_")
    assert len(hash_result) == 71


def test_compute_file_hash_large_file(tmp_path):
    """Test hashing a large file (tests chunked reading)."""
    large_file = tmp_path / "large.txt"

    # Create a file larger than 8KB (chunk size)
    with open(large_file, "w") as f:
        for i in range(10000):
            f.write(f"Line {i}: Some content to make it larger\n")

    hash_result = compute_file_hash(large_file)

    assert hash_result.startswith("sha256_")
    assert len(hash_result) == 71


def test_compute_file_hash_empty_file(tmp_path):
    """Test hashing an empty file."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")

    hash_result = compute_file_hash(empty_file)

    # Should match empty string hash
    expected = "sha256_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert hash_result == expected


def test_compute_file_hash_missing_file():
    """Test that compute_file_hash raises error for missing files."""
    non_existent = Path("/nonexistent/file.txt")

    with pytest.raises(FileNotFoundError, match="File not found"):
        compute_file_hash(non_existent)


def test_compute_file_hash_with_md5(tmp_path):
    """Test file hashing with MD5 algorithm."""
    test_file = tmp_path / "md5test.txt"
    test_file.write_text("MD5 file test")

    hash_result = compute_file_hash(test_file, algorithm="md5")

    assert hash_result.startswith("md5_")
    assert len(hash_result) == 36


# ========================================
# Short Hash Tests
# ========================================


def test_short_hash_with_algorithm_prefix():
    """Test shortening a hash with algorithm prefix."""
    full_hash = "sha256_1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890"

    short = short_hash(full_hash, length=12)

    assert short == "sha256_1a2b3c4d5e6f"


def test_short_hash_default_length():
    """Test short_hash with default length (12)."""
    full_hash = "sha256_abcdefghijklmnopqrstuvwxyz1234567890"

    short = short_hash(full_hash)

    assert short == "sha256_abcdefghijkl"
    assert len(short) == 7 + 12  # 'sha256_' + 12 chars


def test_short_hash_custom_length():
    """Test short_hash with custom length."""
    full_hash = "sha256_0123456789abcdef"

    short = short_hash(full_hash, length=8)

    assert short == "sha256_01234567"


def test_short_hash_without_prefix():
    """Test short_hash on string without algorithm prefix."""
    hash_no_prefix = "1a2b3c4d5e6f7890abcdef"

    short = short_hash(hash_no_prefix, length=12)

    assert short == "1a2b3c4d5e6f"


def test_short_hash_length_longer_than_hash():
    """Test short_hash when requested length exceeds hash length."""
    short_hash_str = "sha256_abc123"

    short = short_hash(short_hash_str, length=50)

    # Should return the hash portion in full
    assert short == "sha256_abc123"


def test_short_hash_zero_length():
    """Test short_hash with zero length."""
    full_hash = "sha256_abcdefgh"

    short = short_hash(full_hash, length=0)

    assert short == "sha256_"


def test_short_hash_md5():
    """Test short_hash with MD5 hash."""
    md5_hash = "md5_9e107d9d372bb6826bd81d3542a419d6"

    short = short_hash(md5_hash, length=8)

    assert short == "md5_9e107d9d"


# ========================================
# Integration Tests
# ========================================


def test_text_and_file_hash_match(tmp_path):
    """Test that hashing text directly matches hashing a file with that text."""
    content = "Test content for comparison"

    # Hash the text directly
    text_hash = compute_text_hash(content)

    # Write to file and hash the file
    test_file = tmp_path / "test.txt"
    test_file.write_text(content, encoding="utf-8")
    file_hash = compute_file_hash(test_file)

    # Should produce the same hash
    assert text_hash == file_hash


def test_hash_workflow_example(tmp_path):
    """Test a realistic workflow using hash functions."""
    # Create a file
    document = tmp_path / "document.pdf"
    document.write_bytes(b"PDF content simulation")

    # Compute full hash
    full_hash = compute_file_hash(document)

    # Get short version for display
    display_hash = short_hash(full_hash, length=8)

    # Verify formats
    assert full_hash.startswith("sha256_")
    assert display_hash.startswith("sha256_")
    assert len(display_hash) == 15  # 'sha256_' (7) + 8 chars

    # Verify consistency
    second_hash = compute_file_hash(document)
    assert full_hash == second_hash
