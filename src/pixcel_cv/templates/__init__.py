"""Template loading utilities."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template


def load_german_cv_template() -> Template:
    """Load German CV LaTeX template.

    Returns:
        Jinja2 template object.
    """
    template_dir = Path(__file__).parent
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        variable_start_string="<VAR>",
        variable_end_string="</VAR>",
        block_start_string="<BLOCK>",
        block_end_string="</BLOCK>",
        comment_start_string="<COMMENT>",
        comment_end_string="</COMMENT>",
        trim_blocks=True,
        lstrip_blocks=True,
        finalize=lambda x: x if x is not None else "",
    )
    return env.get_template("german_cv.tex")
