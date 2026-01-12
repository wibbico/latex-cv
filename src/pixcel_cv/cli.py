"""CLI for CV generation."""

import sys
from pathlib import Path

from .generator import CVGenerator, AnschreibenGenerator
from .loaders import (
    load_cv_from_yaml,
    load_cv_from_yaml_folder,
    load_anschreiben_from_yaml,
    load_anschreiben_from_yaml_folder,
)


def main(
    input_yaml: str | None = None,
    yaml_folder: str | None = None,
    config_folder: str | None = None,
    output_pdf: str | None = None,
    output_latex: str | None = None,
    engine: str = "pdflatex",
    portrait: str | None = None,
    is_anschreiben: bool = False,
) -> int:
    """Generate CV or Anschreiben from YAML file or folder.

    Args:
        input_yaml: Path to input YAML file.
        yaml_folder: Path to folder with YAML files (data).
        config_folder: Optional path to folder with cv_config.yaml.
        output_pdf: Path for output PDF (optional).
        output_latex: Path for output LaTeX (optional).
        engine: LaTeX engine to use.
        portrait: Path to portrait picture file (optional, CV only).
        is_anschreiben: If True, generate Anschreiben instead of CV.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        if input_yaml and yaml_folder:
            print("Error: Cannot specify both input file and --yaml-folder", file=sys.stderr)
            return 1

        if not input_yaml and not yaml_folder:
            print("Error: Must specify either input YAML file or --yaml-folder", file=sys.stderr)
            return 1

        if is_anschreiben:
            # Anschreiben mode
            if yaml_folder:
                folder_path = Path(yaml_folder)
                if not folder_path.exists():
                    print(f"Error: Folder not found: {yaml_folder}", file=sys.stderr)
                    return 1
                print(f"Loading Anschreiben from folder {yaml_folder}...")
                anschreiben = load_anschreiben_from_yaml_folder(folder_path)
            else:
                input_path = Path(input_yaml)
                if not input_path.exists():
                    print(f"Error: Input file not found: {input_yaml}", file=sys.stderr)
                    return 1
                print(f"Loading Anschreiben from {input_yaml}...")
                anschreiben = load_anschreiben_from_yaml(input_path)

            generator = AnschreibenGenerator(anschreiben)

            if output_latex:
                latex_path = Path(output_latex)
                latex_path.parent.mkdir(parents=True, exist_ok=True)
                latex_content = generator.to_latex()
                latex_path.write_text(latex_content, encoding="utf-8")
                print(f"LaTeX exported to {output_latex}")

            if output_pdf:
                pdf_path = Path(output_pdf)
                print(f"Generating PDF using {engine}...")
                generator.to_pdf(pdf_path, engine=engine)
                print(f"PDF generated successfully: {output_pdf}")

            if not output_pdf and not output_latex:
                print("No output specified. Use --pdf or --latex to save output.")
                return 1

            return 0

        else:
            # CV mode
            if yaml_folder:
                folder_path = Path(yaml_folder)
                if not folder_path.exists():
                    print(f"Error: Folder not found: {yaml_folder}", file=sys.stderr)
                    return 1
                print(f"Loading CV from folder {yaml_folder}...")
                if config_folder:
                    config_path = Path(config_folder)
                    if not config_path.exists():
                        print(f"Error: Config folder not found: {config_folder}", file=sys.stderr)
                        return 1
                    print(f"Loading config from {config_folder}...")
                    cv = load_cv_from_yaml_folder(folder_path, config_folder=config_path, portrait_path=portrait)
                else:
                    cv = load_cv_from_yaml_folder(folder_path, portrait_path=portrait)
            else:
                input_path = Path(input_yaml)
                if not input_path.exists():
                    print(f"Error: Input file not found: {input_yaml}", file=sys.stderr)
                    return 1
                print(f"Loading CV from {input_yaml}...")
                cv = load_cv_from_yaml(input_path)

            generator = CVGenerator(cv)

            if output_latex:
                latex_path = Path(output_latex)
                latex_path.parent.mkdir(parents=True, exist_ok=True)
                latex_content = generator.to_latex()
                latex_path.write_text(latex_content, encoding="utf-8")
                print(f"LaTeX exported to {output_latex}")

            if output_pdf:
                pdf_path = Path(output_pdf)
                print(f"Generating PDF using {engine}...")
                generator.to_pdf(pdf_path, engine=engine)
                print(f"PDF generated successfully: {output_pdf}")

            if not output_pdf and not output_latex:
                print("No output specified. Use --pdf or --latex to save output.")
                return 1

            return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate pixel-perfect CVs or Anschreiben from YAML",
        add_help=False  # We'll add help manually to allow flexible parsing
    )
    
    # Try to detect if a subcommand is being used
    import sys
    args_list = sys.argv[1:]
    
    # Check if there's a recognized subcommand
    has_subcommand = any(cmd in args_list for cmd in ['cv', 'anschreiben'])
    
    if has_subcommand:
        # Use subcommand mode
        parser = argparse.ArgumentParser(description="Generate pixel-perfect CVs or Anschreiben from YAML")
        subparsers = parser.add_subparsers(dest="command", help="Command to run")

        # CV subcommand
        cv_parser = subparsers.add_parser("cv", help="Generate CV (default)")
        cv_parser.add_argument("input", nargs="?", help="Input YAML file")
        cv_parser.add_argument("--yaml-folder", help="Folder with YAML data files")
        cv_parser.add_argument(
            "--config-folder", help="Folder with cv_config.yaml (defaults to yaml-folder)"
        )
        cv_parser.add_argument("--pdf", help="Output PDF file path")
        cv_parser.add_argument("--latex", help="Output LaTeX file path")
        cv_parser.add_argument(
            "--engine",
            choices=["pdflatex", "xelatex", "lualatex"],
            default="pdflatex",
            help="LaTeX engine to use",
        )
        cv_parser.add_argument("--portrait", help="Path to portrait picture file")

        # Anschreiben subcommand
        anschreiben_parser = subparsers.add_parser("anschreiben", help="Generate Anschreiben (cover letter)")
        anschreiben_parser.add_argument("input", nargs="?", help="Input YAML file")
        anschreiben_parser.add_argument("--yaml-folder", help="Folder with YAML data files")
        anschreiben_parser.add_argument("--pdf", help="Output PDF file path")
        anschreiben_parser.add_argument("--latex", help="Output LaTeX file path")
        anschreiben_parser.add_argument(
            "--engine",
            choices=["pdflatex", "xelatex", "lualatex"],
            default="pdflatex",
            help="LaTeX engine to use",
        )

        args = parser.parse_args()

        if args.command == "cv":
            sys.exit(
                main(
                    input_yaml=args.input,
                    yaml_folder=args.yaml_folder,
                    config_folder=args.config_folder,
                    output_pdf=args.pdf,
                    output_latex=args.latex,
                    engine=args.engine,
                    portrait=args.portrait,
                    is_anschreiben=False,
                )
            )
        elif args.command == "anschreiben":
            sys.exit(
                main(
                    input_yaml=args.input,
                    yaml_folder=args.yaml_folder,
                    config_folder=None,
                    output_pdf=args.pdf,
                    output_latex=args.latex,
                    engine=args.engine,
                    portrait=None,
                    is_anschreiben=True,
                )
            )
    else:
        # No subcommand: backward-compatible mode for Makefile
        # Auto-detect anschreiben if "anschreiben" is in the input filename
        auto_anschreiben = any("anschreiben" in arg.lower() for arg in args_list if not arg.startswith("-"))
        
        parser.add_argument("input", nargs="?", help="Input YAML file")
        parser.add_argument("--yaml-folder", help="Folder with YAML data files")
        parser.add_argument(
            "--config-folder", help="Folder with cv_config.yaml (defaults to yaml-folder)"
        )
        parser.add_argument("--pdf", help="Output PDF file path")
        parser.add_argument("--latex", help="Output LaTeX file path")
        parser.add_argument(
            "--engine",
            choices=["pdflatex", "xelatex", "lualatex"],
            default="pdflatex",
            help="LaTeX engine to use",
        )
        parser.add_argument("--portrait", help="Path to portrait picture file")
        parser.add_argument("--template", help="Template to use (timeline, etc.)")
        parser.add_argument("-h", "--help", action="help", help="show this help message and exit")

        args = parser.parse_args()

        # If auto-detected as anschreiben, use anschreiben mode
        if auto_anschreiben:
            sys.exit(
                main(
                    input_yaml=args.input,
                    yaml_folder=args.yaml_folder,
                    config_folder=None,
                    output_pdf=args.pdf,
                    output_latex=args.latex,
                    engine=args.engine,
                    portrait=None,
                    is_anschreiben=True,
                )
            )
        else:
            # Default to CV mode
            sys.exit(
                main(
                    input_yaml=args.input,
                    yaml_folder=args.yaml_folder,
                    config_folder=args.config_folder,
                    output_pdf=args.pdf,
                    output_latex=args.latex,
                    engine=args.engine,
                    portrait=args.portrait,
                    is_anschreiben=False,
                )
            )
