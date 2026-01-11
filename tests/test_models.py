"""Tests for pixcel_cv package."""

from datetime import date

import pytest

from pixcel_cv.models import CurriculumVitae, DateRange, ContactInfo, WorkExperience


def test_date_range_format_de():
    """Test German date formatting."""
    # Test with end date
    dr = DateRange(start=date(2020, 3, 15), end=date(2023, 8, 31))
    assert dr.format_de() == "03/2020 – 08/2023"

    # Test with present
    dr = DateRange(start=date(2020, 3, 15), present=True)
    assert dr.format_de() == "03/2020 – heute"

    # Test without end date
    dr = DateRange(start=date(2020, 3, 15))
    assert dr.format_de() == "03/2020"


def test_cv_model_creation():
    """Test CV model validation."""
    cv_data = {
        "contact": {
            "name": "Max Mustermann",
            "email": "max@example.de",
            "phone": "+49 123",
        },
        "berufliches_profil": "Test",
        "work_experience": [],
        "education": [],
        "skills": [],
        "languages": [],
        "certifications": [],
        "custom_sections": {},
    }

    cv = CurriculumVitae(**cv_data)
    assert cv.contact.name == "Max Mustermann"
    assert cv.berufliches_profil == "Test"


def test_cv_model_with_work_experience():
    """Test CV with work experience."""
    cv_data = {
        "contact": {
            "name": "Max Mustermann",
            "email": "max@example.de",
        },
        "work_experience": [
            {
                "title": "Senior Engineer",
                "company": "TechCorp",
                "period": {
                    "start": "2020-03-01",
                    "present": True,
                },
                "highlights": ["Achievement 1"],
            }
        ],
    }

    cv = CurriculumVitae(**cv_data)
    assert len(cv.work_experience) == 1
    assert cv.work_experience[0].title == "Senior Engineer"
    assert cv.work_experience[0].period.present is True
