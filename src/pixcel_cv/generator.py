"""CV generator that converts data models to LaTeX."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from .models import CurriculumVitae
from .templates import load_german_cv_template


def render_cv(cv: CurriculumVitae) -> str:
    """Render CV to LaTeX using template.

    Args:
        cv: The CV model to render.

    Returns:
        LaTeX document string.
    """
    template = load_german_cv_template()
    return template.render(cv=cv)


def compile_to_pdf(cv: CurriculumVitae, output_path: Path, engine: str = "pdflatex") -> None:
    """Render CV and compile to PDF.

    Args:
        cv: The CV model to compile.
        output_path: Path where the PDF should be saved.
        engine: LaTeX engine to use (pdflatex, xelatex, lualatex).

    Raises:
        RuntimeError: If LaTeX compilation fails.
    """
    latex_content = render_cv(cv)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        tex_file = tmp_path / "cv.tex"
        tex_file.write_text(latex_content, encoding="utf-8")

        try:
            # First compilation
            subprocess.run(
                [
                    engine,
                    "-interaction=nonstopmode",
                    "-output-directory",
                    str(tmp_path),
                    str(tex_file),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            # Second compilation for references
            subprocess.run(
                [
                    engine,
                    "-interaction=nonstopmode",
                    "-output-directory",
                    str(tmp_path),
                    str(tex_file),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            pdf_file = tmp_path / "cv.pdf"
            if not pdf_file.exists():
                raise RuntimeError("PDF generation failed: output file not found")

            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf_file, output_path)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"LaTeX compilation failed with {engine}: {e.stderr}") from e
        except FileNotFoundError as e:
            raise RuntimeError(
                f"LaTeX engine '{engine}' not found. "
                f"Please install a LaTeX distribution (e.g., TeX Live, MiKTeX)."
            ) from e


# Legacy class for backward compatibility
class CVGenerator:
    """Generate LaTeX CV from CV model (legacy interface)."""

    def __init__(self, cv: CurriculumVitae) -> None:
        """Initialize CV generator.

        Args:
            cv: The CV model to render.
        """
        self.cv = cv

    def to_latex(self) -> str:
        """Generate LaTeX source from CV model.

        Returns:
            LaTeX document string.
        """
        return render_cv(self.cv)

    def to_pdf(self, output_path: Path, engine: str = "pdflatex") -> None:
        """Generate PDF from CV model.

        Args:
            output_path: Path where the PDF should be saved.
            engine: LaTeX engine to use.
        """
        compile_to_pdf(self.cv, output_path, engine)
