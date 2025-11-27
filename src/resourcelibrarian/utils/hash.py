"""Hashing utilities for content integrity and file tracking."""

import hashlib
from pathlib import Path


def compute_text_hash(text: str, algorithm: str = "sha256") -> str:
    """Compute hash of text content.

    Args:
        text: Text to hash
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hash digest as hex string with algorithm prefix (e.g., 'sha256_abc123...')

    Example:
        >>> compute_text_hash("Hello, World!")
        'sha256_dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
    """
    hasher = hashlib.new(algorithm)
    hasher.update(text.encode("utf-8"))
    digest = hasher.hexdigest()
    return f"{algorithm}_{digest}"


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Compute hash of file content.

    Reads file in chunks to efficiently handle large files.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hash digest as hex string with algorithm prefix (e.g., 'sha256_abc123...')

    Raises:
        FileNotFoundError: If file doesn't exist

    Example:
        >>> compute_file_hash(Path("document.pdf"))
        'sha256_1a2b3c4d5e6f...'
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        # Read in 8KB chunks for efficient large file processing
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    digest = hasher.hexdigest()
    return f"{algorithm}_{digest}"


def short_hash(hash_string: str, length: int = 12) -> str:
    """Get shortened version of a hash for display purposes.

    Args:
        hash_string: Full hash string (e.g., 'sha256_abc123...')
        length: Length of hash portion to keep (default: 12)

    Returns:
        Shortened hash (e.g., 'sha256_abc123')

    Example:
        >>> short_hash('sha256_1a2b3c4d5e6f7890abcdef', 8)
        'sha256_1a2b3c4d'
    """
    if "_" in hash_string:
        algo, digest = hash_string.split("_", 1)
        return f"{algo}_{digest[:length]}"
    return hash_string[:length]
