"""YAML loader for CV data."""

from pathlib import Path
from typing import Any

import yaml

from .models import Certification, ContactInfo, CurriculumVitae, Language, Skill, Anschreiben, PostalAddress


def load_cv_from_yaml(file_path: Path | str) -> CurriculumVitae:
    """Load CV from YAML file.

    Args:
        file_path: Path to YAML file.

    Returns:
        CurriculumVitae model instance.
    """
    file_path = Path(file_path)
    with open(file_path, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)

    return CurriculumVitae(**data)


def load_cv_from_yaml_folder(
    folder_path: Path | str,
    config_folder: Path | str | None = None,
    portrait_path: str | None = None,
) -> CurriculumVitae:
    """Load CV from multiple YAML files in a folder.

    Args:
        folder_path: Path to folder containing YAML files (data files).
        portrait_path: Optional path to portrait picture file.
        config_folder: Optional path to folder containing cv_config.yaml (defaults to folder_path).

    Returns:
        CurriculumVitae model instance.
    """
    folder_path = Path(folder_path)
    if config_folder is None:
        config_folder = folder_path
    else:
        config_folder = Path(config_folder)

    # Load all YAML files - NEW STRUCTURE
    # Data files from primary folder (typically OneDrive)
    cv_basis = _load_yaml_file(folder_path / "cv_basis.yaml") or {}
    berufliche_stationen = _load_yaml_file(folder_path / "berufliche_stationen.yaml") or {}
    basedata = _load_yaml_file(folder_path / "basedata.yaml") or {}
    missionstatement = _load_yaml_file(folder_path / "missionstatement.yaml") or []
    skills_data = _load_yaml_file(folder_path / "skills.yaml") or {"skills": []}
    projects = _load_yaml_file(folder_path / "projekt_historie.yaml") or {"projects": []}
    certifications_data = _load_yaml_file(folder_path / "certifications.yaml") or {"certifications": []}
    
    # Config file from config folder (typically local ./yaml)
    cv_config = _load_yaml_file(config_folder / "cv_config.yaml") or {}

    # Build contact info from cv_basis.yaml (NEW STRUCTURE)
    persoenliche_daten = cv_basis.get("persoenliche_daten", {})

    # Fallback to old structure if cv_basis doesn't exist
    if not persoenliche_daten:
        profile = basedata.get("profile_data", {})
        persoenliche_daten = {
            "name": profile.get("name", {}).get("de", ""),
            "email": profile.get("email", ""),
            "telefon": profile.get("phone", ""),
            "adresse": profile.get("location", {}).get("de", ""),
        }

    # Use provided portrait_path or load from cv_config
    portrait = portrait_path or cv_config.get("portrait_path")

    contact = ContactInfo(
        name=persoenliche_daten.get("name", ""),
        email=persoenliche_daten.get("email", ""),
        title=persoenliche_daten.get("titel") or basedata.get("profile_data", {}).get("title", {}).get("de", ""),
        phone=persoenliche_daten.get("telefon", ""),
        location=f"{persoenliche_daten.get('adresse', '')}, {persoenliche_daten.get('plz_ort', '')}".strip(
            ", "
        ),
        website=basedata.get("profile_data", {}).get("website", ""),
        linkedin=persoenliche_daten.get("linkedin", "") or basedata.get("profile_data", {}).get("linkedin", ""),
        github=persoenliche_daten.get("github", "") or basedata.get("profile_data", {}).get("github", ""),
        portrait_path=portrait,
    )

    # Build professional profile - prefer short version from cv_basis
    berufliches_profil = ""
    
    cv_sections = cv_basis.get("sections", {})
    berufliches_profil = cv_sections.get("berufliches_profil", {}).get("de", "")
    
    # Build skills from skills.yaml - group by category
    skills_by_category: dict[str, list[str]] = {}
    if skills_data.get("skills"):
        for skill in skills_data["skills"]:
            category = skill.get("category", "Sonstige")
            title = skill.get("title", "")
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(title)

    # Convert to skills list
    skills_list = [
        Skill(category=cat, items=items) for cat, items in sorted(skills_by_category.items())
    ]

    # Build languages
    languages = [
        Language(name="Deutsch", level="Muttersprache"),
        Language(name="Englisch", level="Fließend"),
    ]

    # Create custom sections for additional content
    custom_sections: dict[str, str] = {}

    # Add work experience section (NEW STRUCTURE)
    stationen = berufliche_stationen.get("berufliche_stationen", [])
    if stationen:
        work_text = ""
        for station in stationen:
            position = station.get("position", "")
            unternehmen = station.get("unternehmen", "")
            ort = station.get("ort", "")
            start = station.get("start", "")
            bis = station.get("bis", "")

            # Escape LaTeX
            position_safe = _escape_latex(position)
            unternehmen_safe = _escape_latex(unternehmen)
            ort_safe = _escape_latex(ort)
            start_safe = _escape_latex(start)
            bis_safe = _escape_latex(bis)

            # Build entry
            work_text += f"\\textbf{{{position_safe}}} \\\\\n"
            work_text += f"{unternehmen_safe}"
            if ort:
                work_text += f", {ort_safe}"
            work_text += f" ({start_safe} -- {bis_safe})\n\n"

            # Add Schwerpunkte if available
            if station.get("schwerpunkte"):
                work_text += "\\textit{Schwerpunkte:}\n"
                work_text += "\\begin{itemize}\n"
                for sp in station.get("schwerpunkte", []):
                    work_text += f"  \\item {_escape_latex(sp)}\n"
                work_text += "\\end{itemize}\n"

            # Add Aufgaben if available
            if station.get("aufgaben"):
                work_text += "\\textit{Aufgaben:}\n"
                work_text += "\\begin{itemize}\n"
                for aufgabe in station.get("aufgaben", []):
                    work_text += f"  \\item {_escape_latex(aufgabe)}\n"
                work_text += "\\end{itemize}\n"

            # Add Tätigkeit if available (fallback for simpler entries)
            if station.get("tätigkeit") and not station.get("aufgaben"):
                work_text += f"{_escape_latex(station.get('tätigkeit', ''))}\n"

            # Add Hauptprojekt if available
            if station.get("hauptprojekt"):
                work_text += f"\\textit{{Hauptprojekt:}} {_escape_latex(station.get('hauptprojekt', ''))}\n"

            # Add Projektaufgaben if available
            if station.get("projektaufgaben"):
                work_text += "\\begin{itemize}\n"
                for pa in station.get("projektaufgaben", []):
                    work_text += f"  \\item {_escape_latex(pa)}\n"
                work_text += "\\end{itemize}\n"

            # Add spacing between entries
            work_text += "\n"

        if work_text:
            custom_sections["Beruflicher Werdegang"] = work_text.strip()

    # Add education section (NEW STRUCTURE)
    bildungsweg = cv_basis.get("bildungsweg", [])
    if bildungsweg:
        education_text = ""
        for bildung in bildungsweg:
            institution = bildung.get("institution", "")
            abschluss = bildung.get("abschluss", "")
            jahr = bildung.get("jahr", "")
            ort = bildung.get("ort", "")
            schwerpunkte = bildung.get("schwerpunkte", [])
            gesamtnote = bildung.get("gesamtnote", "")

            # Escape LaTeX
            institution_safe = _escape_latex(institution)
            abschluss_safe = _escape_latex(abschluss)
            jahr_safe = _escape_latex(jahr)
            ort_safe = _escape_latex(ort) if ort else ""
            gesamtnote_safe = _escape_latex(gesamtnote) if gesamtnote else ""

            # Build entry
            education_text += f"\\textbf{{{abschluss_safe}}} \\\\\n"
            education_text += f"{institution_safe}"
            if ort:
                education_text += f", {ort_safe}"
            if jahr:
                education_text += f" ({jahr_safe})"
            education_text += "\n"

            # Add Schwerpunkte if available
            if schwerpunkte:
                education_text += "\\textit{Schwerpunkte:} "
                education_text += ", ".join([_escape_latex(sp) for sp in schwerpunkte])
                education_text += "\n"

            # Add Gesamtnote if available
            if gesamtnote:
                education_text += f"\\textit{{Gesamtnote:}} {gesamtnote_safe}\n"

            # Add spacing between entries
            education_text += "\n"

        if education_text:
            custom_sections["Bildungsweg"] = education_text.strip()

    # Add availability info
    profile = basedata.get("profile_data", {})
    availability_text = _build_availability_section(profile)
    if availability_text:
        custom_sections["Verfügbarkeit"] = availability_text

    # Add projects as a custom section
    projects_list = projects.get("projects", [])

    # Filter projects by include_in_cv flag (DEFAULT TO FALSE)
    filtered_projects = [p for p in projects_list if p.get("include_in_cv", False)]

    if filtered_projects:
        projects_text = ""
        for project in filtered_projects:
            title = project.get("project_de", "")
            period_from = project.get("period_from", "")
            period_to = project.get("period_to", "")
            description = project.get("description_de", "")
            tools = ", ".join(project.get("tools_libraries", []))

            if title:
                # Escape special LaTeX characters
                title_safe = _escape_latex(title)
                period_from_safe = _escape_latex(str(period_from))
                period_to_safe = _escape_latex(str(period_to))
                # Convert bullet points to proper LaTeX itemize lists
                description_safe = _convert_bullets_to_itemize(description)
                tools_safe = _escape_latex(tools)

                projects_text += (
                    f"\\textbf{{{title_safe}}} ({period_from_safe} -- {period_to_safe})\n\n"
                )
                if description_safe:
                    projects_text += f"{description_safe}\n\n"
                if tools_safe:
                    projects_text += f"\\textit{{Technologien: {tools_safe}}}\n\n"

        if projects_text:
            custom_sections["Referenzprojekte"] = projects_text.strip()

    # Process certifications from YAML
    certifications_list = []
    for cert in certifications_data.get("certifications", []):
        try:
            # Parse date if provided, otherwise use None
            cert_date = cert.get("date")
            if cert_date:
                # Try to parse as date (YYYY-MM-DD format)
                from datetime import datetime
                if isinstance(cert_date, str):
                    cert_date = datetime.strptime(cert_date, "%Y-%m-%d").date()
            else:
                # If no date, use today's date as fallback
                from datetime import date
                cert_date = date.today()
            
            certification = Certification(
                title=cert.get("title", ""),
                issuer=cert.get("issuer", ""),
                date=cert_date,
                credential_id=cert.get("credential_id"),
                credential_url=cert.get("credential_url"),
            )
            certifications_list.append(certification)
        except Exception:
            # Skip invalid certifications
            pass

    # Create CurriculumVitae instance
    cv = CurriculumVitae(
        contact=contact,
        berufliches_profil=berufliches_profil,
        work_experience=[],
        education=[],
        skills=skills_list,
        languages=languages,
        certifications=certifications_list,
        education_history=custom_sections.get("Bildungsweg", ""),
        projects=custom_sections.get("Referenzprojekte", ""),
        availability=custom_sections.get("Verfügbarkeit", ""),
        custom_sections=custom_sections,
    )

    return cv


def _load_yaml_file(file_path: Path) -> dict[str, Any] | list[Any] | None:
    """Load a single YAML file.

    Args:
        file_path: Path to YAML file.

    Returns:
        Parsed YAML content or None if file doesn't exist.
    """
    if not file_path.exists():
        return None

    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_availability_section(profile: dict) -> str:
    """Build availability information section.

    Args:
        profile: Profile data dictionary.

    Returns:
        Formatted availability text.
    """
    lines = []

    if profile.get("available_from"):
        available = profile.get("available_from", {})
        if isinstance(available, dict):
            available_de = available.get("de", "")
        else:
            available_de = str(available)
        if available_de:
            lines.append(f"\\textbf{{Verfügbar ab:}} {_escape_latex(available_de)}")

    if profile.get("availability_notice_period"):
        notice = profile.get("availability_notice_period", {})
        if isinstance(notice, dict):
            notice_de = notice.get("de", "")
        else:
            notice_de = str(notice)
        if notice_de:
            lines.append(f"\\textbf{{Kündigungsfrist:}} {_escape_latex(notice_de)}")

    if profile.get("willing_to_travel"):
        travel = profile.get("willing_to_travel", {})
        if isinstance(travel, dict):
            travel_de = travel.get("de", "")
        else:
            travel_de = str(travel)
        if travel_de:
            lines.append(f"\\textbf{{Bereitschaft zu Reisen:}} {_escape_latex(travel_de)}")

    if profile.get("employment_status"):
        status = profile.get("employment_status", {})
        if isinstance(status, dict):
            status_de = status.get("de", "")
        else:
            status_de = str(status)
        if status_de:
            lines.append(f"\\textbf{{Beschäftigungsart:}} {_escape_latex(status_de)}")

    return " \\newline ".join(lines) if lines else ""


def _convert_bullets_to_itemize(text: str) -> str:
    """Convert bullet points (- prefix) to LaTeX itemize list.

    Args:
        text: Text potentially containing bullet points.

    Returns:
        Text with bullet points converted to LaTeX itemize list.
    """
    lines = text.split("\n")
    result_parts: list[str] = []
    bullet_items: list[str] = []
    current_text: list[str] = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            # Found a bullet point
            if current_text:
                # Flush accumulated text with LaTeX line breaks preserved
                text_part = " \\\\ ".join([_escape_latex(t) for t in current_text])
                result_parts.append(text_part)
                current_text = []
            # Collect bullet item
            bullet_items.append(_escape_latex(stripped[2:].strip()))
        else:
            if bullet_items:
                # Flush accumulated bullets
                bullet_text = "\\begin{itemize}\n"
                for item in bullet_items:
                    bullet_text += f"  \\item {item}\n"
                bullet_text += "\\end{itemize}"
                result_parts.append(bullet_text)
                bullet_items = []
            # Add regular text
            if stripped:
                current_text.append(stripped)
    
    # Flush any remaining content
    if bullet_items:
        bullet_text = "\\begin{itemize}\n"
        for item in bullet_items:
            bullet_text += f"  \\item {item}\n"
        bullet_text += "\\end{itemize}"
        result_parts.append(bullet_text)
    elif current_text:
        # Preserve line breaks in remaining text
        text_part = " \\\\ ".join([_escape_latex(t) for t in current_text])
        result_parts.append(text_part)
    
    return "\n\n".join(result_parts)


def _escape_latex(text: str, preserve_linebreaks: bool = False) -> str:
    """Escape special LaTeX characters.

    Args:
        text: Text to escape.
        preserve_linebreaks: If True, preserve newlines as LaTeX linebreak commands.

    Returns:
        Escaped text safe for LaTeX.
    """
    # Preserve linebreaks before escaping if requested
    if preserve_linebreaks:
        # Split by newlines, escape each line, then rejoin with LaTeX linebreak
        lines = text.split("\n")
        escaped_lines = []
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespace from each line
            if line:  # Only add non-empty lines
                # Escape special LaTeX characters in the line
                line = line.replace("\\", "\\textbackslash{}")
                line = line.replace("{", "\\{")
                line = line.replace("}", "\\}")
                line = line.replace("$", "\\$")
                line = line.replace("&", "\\&")
                line = line.replace("%", "\\%")
                line = line.replace("#", "\\#")
                line = line.replace("_", "\\_")
                line = line.replace("^", "\\^{}")
                line = line.replace("~", "\\textasciitilde{}")
                escaped_lines.append(line)
        return " \\\\ ".join(escaped_lines)
    
    # Standard escaping without preserving linebreaks
    text = text.replace("\\", "\\textbackslash{}")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("$", "\\$")
    text = text.replace("&", "\\&")
    text = text.replace("%", "\\%")
    text = text.replace("#", "\\#")
    text = text.replace("_", "\\_")
    text = text.replace("^", "\\^{}")
    text = text.replace("~", "\\textasciitilde{}")
    return text


def save_cv_to_yaml(cv: CurriculumVitae, file_path: Path | str) -> None:
    """Save CV to YAML file.

    Args:
        cv: CurriculumVitae model instance.
        file_path: Path where YAML should be saved.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(cv.model_dump(), f, allow_unicode=True, default_flow_style=False)

def load_anschreiben_from_yaml(file_path: Path | str) -> Anschreiben:
    """Load Anschreiben (cover letter) from YAML file.

    Args:
        file_path: Path to YAML file containing cover letter data.

    Returns:
        Anschreiben model instance.
    """
    file_path = Path(file_path)
    with open(file_path, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)

    # Parse contact info - try from anschreiben.yaml first, then cv_basis.yaml
    contact_data = data.get("contact", {})
    
    # If contact info is missing, try to load from cv_basis.yaml in the same directory
    if not contact_data and "name" not in contact_data and "email" not in contact_data:
        cv_basis_path = file_path.parent / "cv_basis.yaml"
        if cv_basis_path.exists():
            cv_basis = _load_yaml_file(cv_basis_path) or {}
            persoenliche_daten = cv_basis.get("persoenliche_daten", {})
            
            # Map German field names to contact info fields
            if "name" in persoenliche_daten:
                contact_data["name"] = persoenliche_daten["name"]
            if "email" in persoenliche_daten:
                contact_data["email"] = persoenliche_daten["email"]
            if "telefon" in persoenliche_daten:
                contact_data["phone"] = persoenliche_daten["telefon"]
    
    contact = ContactInfo(**contact_data)

    # Parse sender address - try from anschreiben.yaml first, then cv_basis.yaml
    sender_address_data = data.get("sender_address", {})
    
    if not sender_address_data:
        cv_basis_path = file_path.parent / "cv_basis.yaml"
        if cv_basis_path.exists():
            cv_basis = _load_yaml_file(cv_basis_path) or {}
            persoenliche_daten = cv_basis.get("persoenliche_daten", {})
            
            # Map German field names
            if "adresse" in persoenliche_daten:
                sender_address_data["street"] = persoenliche_daten["adresse"]
            if "plz_ort" in persoenliche_daten:
                sender_address_data["postal_city"] = persoenliche_daten["plz_ort"]
    
    sender_address = None
    if sender_address_data:
        sender_address = PostalAddress(**sender_address_data)

    # Extract all fields
    anschreiben_data = {
        "contact": contact,
        "sender_address": sender_address,
        "company_name": data.get("company_name", ""),
        "company_department": data.get("company_department"),
        "contact_person": data.get("contact_person"),
        "company_street": data.get("company_street"),
        "company_postal_code": data.get("company_postal_code"),
        "company_city": data.get("company_city"),
        "position": data.get("position", ""),
        "job_reference": data.get("job_reference"),
        "date": data.get("date", ""),
        "subject": data.get("subject", ""),
        "opening": data.get("opening", ""),
        "body_paragraphs": data.get("body_paragraphs", []),
        "closing": data.get("closing", ""),
        "signature": data.get("signature", "Mit freundlichen Grüßen"),
        "attachments": data.get("attachments", []),
        "pdf_title": data.get("pdf_title"),
        "pdf_author": data.get("pdf_author"),
        "pdf_subject": data.get("pdf_subject"),
        "pdf_keywords": data.get("pdf_keywords"),
    }

    return Anschreiben(**anschreiben_data)


def load_anschreiben_from_yaml_folder(
    folder_path: Path | str,
    anschreiben_file: str = "anschreiben.yaml",
) -> Anschreiben:
    """Load Anschreiben from YAML file with contact info merged from cv_basis.yaml and basedata.yaml.

    Args:
        folder_path: Path to folder containing YAML files.
        anschreiben_file: Name of the anschreiben file (default: anschreiben.yaml).

    Returns:
        Anschreiben model instance.
    """
    folder_path = Path(folder_path)

    # Load cv_basis for contact information (primary source for anschreiben)
    cv_basis = _load_yaml_file(folder_path / "cv_basis.yaml") or {}
    persoenliche_daten = cv_basis.get("persoenliche_daten", {})

    # Load basedata for fallback data
    basedata = _load_yaml_file(folder_path / "basedata.yaml") or {}
    profile_data = basedata.get("profile_data", {})

    # Load anschreiben-specific data
    anschreiben_file_path = folder_path / anschreiben_file
    with open(anschreiben_file_path, encoding="utf-8") as f:
        anschreiben_data: dict[str, Any] = yaml.safe_load(f) or {}

    # Merge contact info from cv_basis (persoenliche_daten) first, then basedata
    contact_data = anschreiben_data.get("contact", {})

    if "name" not in contact_data and "name" in persoenliche_daten:
        contact_data["name"] = persoenliche_daten["name"]
    elif "name" not in contact_data and "name" in profile_data:
        name_data = profile_data["name"]
        contact_data["name"] = name_data.get("de") or name_data.get("en") or ""

    if "email" not in contact_data and "email" in persoenliche_daten:
        contact_data["email"] = persoenliche_daten["email"]
    elif "email" not in contact_data:
        metadata = basedata.get("metadata", {})
        pdf_author = metadata.get("pdf_author", {})
        if isinstance(pdf_author, dict):
            pdf_author = pdf_author.get("de", "")
        # Extract email from "Name (email@example.com)" format
        if "(" in pdf_author and ")" in pdf_author:
            email = pdf_author.split("(")[1].split(")")[0]
            contact_data["email"] = email

    if "phone" not in contact_data and "telefon" in persoenliche_daten:
        contact_data["phone"] = persoenliche_daten["telefon"]

    contact = ContactInfo(**contact_data)

    # Extract sender address from cv_basis or anschreiben data
    sender_address = anschreiben_data.get("sender_address")
    if not sender_address:
        sender_address = {}
        if "adresse" in persoenliche_daten:
            sender_address["street"] = persoenliche_daten["adresse"]
        if "plz_ort" in persoenliche_daten:
            sender_address["postal_city"] = persoenliche_daten["plz_ort"]

    sender_postal_address = PostalAddress(
        street=sender_address.get("street"),
        postal_city=sender_address.get("postal_city"),
    )

    # Build complete anschreiben data
    pdf_generator = anschreiben_data.get("pdf_generator")
    if not pdf_generator:
        # Try cv_basis first
        cv_config = cv_basis.get("cv_config", {})
        pdf_gen_data = cv_config.get("pdf_generator", {})
        if isinstance(pdf_gen_data, dict):
            pdf_generator = pdf_gen_data.get("de") or pdf_gen_data.get("en")
        else:
            pdf_generator = pdf_gen_data or ""
        # Fall back to basedata if not in cv_basis
        if not pdf_generator:
            metadata = basedata.get("metadata", {})
            pdf_gen_data = metadata.get("pdf_generator", {})
            if isinstance(pdf_gen_data, dict):
                pdf_generator = pdf_gen_data.get("de") or pdf_gen_data.get("en")
            else:
                pdf_generator = pdf_gen_data

    # Auto-generate PDF metadata if not provided
    pdf_title = anschreiben_data.get("pdf_title")
    if not pdf_title:
        position = anschreiben_data.get("position", "")
        pdf_title = f"Bewerbung {contact.name} - {position}" if position else f"Bewerbung {contact.name}"

    pdf_author = anschreiben_data.get("pdf_author") or contact.name

    pdf_subject = anschreiben_data.get("pdf_subject")
    if not pdf_subject:
        position = anschreiben_data.get("position", "")
        company = anschreiben_data.get("company_name", "")
        if position and company:
            pdf_subject = f"Bewerbung als {position} bei {company}"
        elif position:
            pdf_subject = f"Bewerbung als {position}"
        else:
            pdf_subject = f"Bewerbung {contact.name}"

    pdf_keywords = anschreiben_data.get("pdf_keywords")
    if not pdf_keywords:
        position = anschreiben_data.get("position", "")
        company = anschreiben_data.get("company_name", "")
        keywords = ["Bewerbung"]
        if position:
            keywords.append(position)
        if company:
            keywords.append(company)
        pdf_keywords = ", ".join(keywords)

    final_data = {
        "contact": contact,
        "sender_address": sender_postal_address,
        "company_name": anschreiben_data.get("company_name", ""),
        "contact_person": anschreiben_data.get("contact_person"),
        "anrede": anschreiben_data.get("anrede"),
        "company_street": anschreiben_data.get("company_street"),
        "company_postal_code": anschreiben_data.get("company_postal_code"),
        "company_city": anschreiben_data.get("company_city"),
        "kennziffer": anschreiben_data.get("kennziffer"),
        "via": anschreiben_data.get("via"),
        "position": anschreiben_data.get("position", ""),
        "date": anschreiben_data.get("date", ""),
        "subject": anschreiben_data.get("subject", ""),
        "opening": anschreiben_data.get("opening", ""),
        "body_paragraphs": anschreiben_data.get("body_paragraphs", []),
        "closing": anschreiben_data.get("closing", ""),
        "signature": anschreiben_data.get("signature", ""),
        "attachments": anschreiben_data.get("attachments", []),
        "pdf_title": pdf_title,
        "pdf_author": pdf_author,
        "pdf_subject": pdf_subject,
        "pdf_keywords": pdf_keywords,
        "pdf_generator": pdf_generator,
    }

    # Strict DIN letter needs sender + recipient postal address for window field.
    if not sender_postal_address.street or not sender_postal_address.postal_city:
        raise ValueError(
            "DIN 5008 Anschreiben requires sender postal address (sender_address.street and sender_address.postal_city). "
            "Provide these in anschreiben YAML or in cv_basis.yaml under persoenliche_daten (adresse, plz_ort)."
        )

    if (
        not final_data.get("company_street")
        or not final_data.get("company_postal_code")
        or not final_data.get("company_city")
    ):
        raise ValueError(
            "DIN 5008 Anschreiben requires recipient postal address for the address window: "
            "company_street, company_postal_code, company_city."
        )

    return Anschreiben(**final_data)