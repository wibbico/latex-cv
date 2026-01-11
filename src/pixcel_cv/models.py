"""CV data models using Pydantic for type safety and validation."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ContactInfo(BaseModel):
    """Contact information section."""

    name: str
    email: str
    title: str | None = None
    phone: str | None = None
    location: str | None = None
    website: str | None = None
    linkedin: str | None = None
    github: str | None = None


class DateRange(BaseModel):
    """Date range for work/education periods."""

    start: date
    end: date | None = None
    present: bool = False

    def format_de(self) -> str:
        """Format date range in German style (MM/YYYY)."""
        start_str = self.start.strftime("%m/%Y")
        if self.present:
            return f"{start_str} – heute"
        elif self.end:
            end_str = self.end.strftime("%m/%Y")
            return f"{start_str} – {end_str}"
        return start_str


class WorkExperience(BaseModel):
    """Work experience entry."""

    title: str
    company: str
    location: str | None = None
    period: DateRange
    description: str | None = None
    highlights: list[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""

    degree: str
    institution: str
    field: str | None = None
    location: str | None = None
    period: DateRange
    grade: str | None = None
    details: str | None = None


class Skill(BaseModel):
    """Skill entry."""

    category: str
    items: list[str]


class Language(BaseModel):
    """Language proficiency."""

    name: str
    level: str  # e.g., "Native", "Fluent", "Professional", "Basic"


class Certification(BaseModel):
    """Certification or achievement."""

    title: str
    issuer: str
    date: date
    credential_id: str | None = None
    credential_url: str | None = None


class CurriculumVitae(BaseModel):
    """Complete CV document."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contact": {
                    "name": "Max Mustermann",
                    "email": "max@example.de",
                    "phone": "+49 123 456789",
                    "location": "Berlin, Deutschland",
                },
                "berufliches_profil": "Erfahrener Data Engineer mit Expertise in Azure...",
                "work_experience": [],
                "education": [],
                "skills": [],
                "languages": [],
                "certifications": [],
                "custom_sections": {},
            }
        }
    )

    contact: ContactInfo
    berufliches_profil: str | None = None
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    education_history: str = ""  # Formatted education/Bildungsweg from YAML
    projects: str = ""  # Formatted projects/Referenzprojekte from YAML
    availability: str = ""  # Availability/Verfügbarkeit from YAML
    custom_sections: dict[str, str] = Field(default_factory=dict)
