#!/usr/bin/env python3
"""Сборка статического сайта: Jinja2-шаблоны → dist/."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"
DIST_DIR = ROOT / "dist"
ASSETS_DIR = ROOT / "assets"

PAGES = (
    {
        "template": "index.ru.html",
        "output": DIST_DIR / "index.html",
        "lang": "ru",
        "assets_prefix": "assets/",
        "lang_href_ru": "index.html",
        "lang_href_en": "en/index.html",
    },
    {
        "template": "index.en.html",
        "output": DIST_DIR / "en" / "index.html",
        "lang": "en",
        "assets_prefix": "../assets/",
        "lang_href_ru": "../index.html",
        "lang_href_en": "index.html",
    },
)


def create_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def copy_assets() -> None:
    target = DIST_DIR / "assets"
    if ASSETS_DIR.exists():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(ASSETS_DIR, target)
    else:
        target.mkdir(parents=True, exist_ok=True)


def build_page(env: Environment, page: dict) -> Path:
    template = env.get_template(page["template"])
    html = template.render(
        lang=page["lang"],
        assets_prefix=page["assets_prefix"],
        lang_href_ru=page["lang_href_ru"],
        lang_href_en=page["lang_href_en"],
    )
    output_path: Path = page["output"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def build() -> list[Path]:
    if not TEMPLATES_DIR.is_dir():
        raise FileNotFoundError(f"Папка шаблонов не найдена: {TEMPLATES_DIR}")

    env = create_environment()
    copy_assets()
    return [build_page(env, page) for page in PAGES]


def main() -> int:
    try:
        outputs = build()
    except Exception as exc:
        print(f"Ошибка сборки: {exc}", file=sys.stderr)
        return 1

    print("Сборка завершена:")
    for path in outputs:
        print(f"  -> {path.relative_to(ROOT)}")

    print("\nЛокальный просмотр:")
    print("  python -m http.server --directory dist")
    print("  RU: http://localhost:8000/")
    print("  EN: http://localhost:8000/en/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
