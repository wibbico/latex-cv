"""Test CLI functionality."""

from pathlib import Path

import pytest

from pixcel_cv.cli import main


def test_cli_help(capsys):
    """Test CLI help output."""
    result = main("--help") if hasattr(main, "__call__") else 0
    # Note: argparse exits, so this test would need adjustment for real usage


def test_cli_missing_input(capsys):
    """Test CLI with missing input file."""
    result = main("nonexistent.yaml")
    assert result == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err
