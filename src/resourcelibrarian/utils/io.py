"""I/O utilities for loading and saving manifests and catalog data."""

import json
from pathlib import Path
from typing import Any

import yaml

from resourcelibrarian.models import BookManifest, VideoManifest


def load_yaml(file_path: Path) -> dict[str, Any]:
    """Load a YAML file.

    Args:
        file_path: Path to YAML file

    Returns:
        Dictionary containing YAML data

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: dict[str, Any], file_path: Path) -> None:
    """Save data to a YAML file.

    Args:
        data: Dictionary to save
        file_path: Path to save YAML file

    Note:
        Creates parent directories if they don't exist
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def load_json(file_path: Path) -> dict[str, Any]:
    """Load a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary containing JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON parsing fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict[str, Any], file_path: Path, indent: int = 2) -> None:
    """Save data to a JSON file.

    Args:
        data: Dictionary to save
        file_path: Path to save JSON file
        indent: JSON indentation level (default: 2)

    Note:
        Creates parent directories if they don't exist
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_book_manifest(folder_path: Path) -> BookManifest:
    """Load a book manifest from a folder.

    Args:
        folder_path: Path to book folder containing manifest.yaml

    Returns:
        BookManifest instance

    Raises:
        FileNotFoundError: If manifest.yaml doesn't exist
        yaml.YAMLError: If YAML parsing fails
        pydantic.ValidationError: If manifest data is invalid
    """
    manifest_path = folder_path / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.yaml found in {folder_path}")

    data = load_yaml(manifest_path)
    return BookManifest(**data)


def save_book_manifest(manifest: BookManifest, folder_path: Path) -> None:
    """Save a book manifest to a folder.

    Args:
        manifest: BookManifest to save
        folder_path: Path to book folder

    Note:
        Saves as manifest.yaml in the folder
        Creates folder if it doesn't exist
    """
    manifest_path = folder_path / "manifest.yaml"
    save_yaml(manifest.to_yaml_dict(), manifest_path)


def load_video_manifest(folder_path: Path) -> VideoManifest:
    """Load a video manifest from a folder.

    Args:
        folder_path: Path to video folder containing manifest.yaml

    Returns:
        VideoManifest instance

    Raises:
        FileNotFoundError: If manifest.yaml doesn't exist
        yaml.YAMLError: If YAML parsing fails
        pydantic.ValidationError: If manifest data is invalid
    """
    manifest_path = folder_path / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.yaml found in {folder_path}")

    data = load_yaml(manifest_path)
    return VideoManifest(**data)


def save_video_manifest(manifest: VideoManifest, folder_path: Path) -> None:
    """Save a video manifest to a folder.

    Args:
        manifest: VideoManifest to save
        folder_path: Path to video folder

    Note:
        Saves as manifest.yaml in the folder
        Creates folder if it doesn't exist
    """
    manifest_path = folder_path / "manifest.yaml"
    save_yaml(manifest.to_yaml_dict(), manifest_path)
