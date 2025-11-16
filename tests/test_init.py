"""Tests for package initialization."""


def test_import():
    """Test that package imports successfully."""
    import resourcelibrarian

    assert resourcelibrarian is not None


def test_version():
    """Test that version is defined."""
    import resourcelibrarian

    assert hasattr(resourcelibrarian, "__version__")
    assert resourcelibrarian.__version__ == "0.1.0"
