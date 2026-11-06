from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def get_env(base_file: str) -> Environment:
    """base_file — обычно __file__ вызывающего модуля."""
    templates_dir = Path(base_file).resolve().parent / "templates"
    return Environment(loader=FileSystemLoader(templates_dir), undefined=StrictUndefined)
