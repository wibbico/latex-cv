"""Test CV generation."""

from pixcel_cv.models import CurriculumVitae, ContactInfo
from pixcel_cv.generator import CVGenerator


def test_generator_to_latex():
    """Test LaTeX generation from CV model."""
    cv = CurriculumVitae(
        contact=ContactInfo(name="Max Mustermann", email="max@example.de")
    )

    generator = CVGenerator(cv)
    latex = generator.to_latex()

    assert r"\documentclass" in latex
    assert "Max Mustermann" in latex
    assert "max@example.de" in latex
