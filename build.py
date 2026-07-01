#!/usr/bin/env python3
"""Сборка статического сайта: Jinja2-шаблоны → dist/."""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image

ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"
DIST_DIR = ROOT / "dist"
ASSETS_DIR = ROOT / "assets"
IMAGES_DIR_NAME = "images"

# Абсолютный URL сайта для Open Graph и canonical.
# Локально: пусто или вручную. В CI: задаётся GitHub Actions (см. .github/workflows/pages.yml).
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "").strip()
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
IMAGE_SIZE_RULES: tuple[tuple[re.Pattern[str], tuple[int, int]], ...] = (
    (re.compile(r"avatar", re.IGNORECASE), (400, 400)),
    (re.compile(r"og", re.IGNORECASE), (1200, 630)),
    (re.compile(r"project", re.IGNORECASE), (1200, 675)),
)
DEFAULT_MAX_SIZE = (1920, 1920)
JPEG_QUALITY = 85
PNG_COMPRESS_LEVEL = 6

PAGES = (
    {
        "template": "index.ru.html",
        "output": DIST_DIR / "index.html",
        "lang": "ru",
        "assets_prefix": "assets/",
        "lang_href_ru": "index.html",
        "lang_href_en": "en/index.html",
        "page_path": "/",
        "og_image": "assets/images/og-placeholder.svg",
    },
    {
        "template": "index.en.html",
        "output": DIST_DIR / "en" / "index.html",
        "lang": "en",
        "assets_prefix": "../assets/",
        "lang_href_ru": "../index.html",
        "lang_href_en": "index.html",
        "page_path": "/en/",
        "og_image": "../assets/images/og-placeholder.svg",
    },
)

def absolute_url(base: str, path: str) -> str:
    base = base.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return f"{base}{path}" if base else ""


def page_context(page: dict) -> dict:
    base = SITE_BASE_URL.rstrip("/")
    page_path = page["page_path"]
    canonical = absolute_url(base, page_path) if base else ""
    og_image_path = page["og_image"].removeprefix("../") if base else page["og_image"]
    og_image = absolute_url(base, f"/{og_image_path.lstrip('/')}") if base else ""
    return {
        "lang": page["lang"],
        "assets_prefix": page["assets_prefix"],
        "lang_href_ru": page["lang_href_ru"],
        "lang_href_en": page["lang_href_en"],
        "canonical_url": canonical,
        "og_image_url": og_image,
    }


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


def max_size_for(path: Path) -> tuple[int, int]:
    for pattern, size in IMAGE_SIZE_RULES:
        if pattern.search(path.stem):
            return size
    return DEFAULT_MAX_SIZE


def optimize_raster_images(images_dir: Path) -> list[str]:
    """Сжимает PNG/JPEG в dist/ при сборке. Исходники в assets/ не трогает."""
    if not images_dir.is_dir():
        return []

    reports: list[str] = []
    for path in sorted(images_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in RASTER_SUFFIXES:
            continue

        before = path.stat().st_size
        max_w, max_h = max_size_for(path)

        with Image.open(path) as img:
            img.load()
            resized = img.copy()
            resized.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

            suffix = path.suffix.lower()
            if suffix in {".jpg", ".jpeg"}:
                if resized.mode != "RGB":
                    resized = resized.convert("RGB")
                resized.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)
            elif suffix == ".png":
                if resized.mode == "P":
                    resized = resized.convert("RGBA")
                resized.save(
                    path,
                    "PNG",
                    optimize=True,
                    compress_level=PNG_COMPRESS_LEVEL,
                )
            elif suffix == ".webp":
                resized.save(path, "WEBP", quality=JPEG_QUALITY, method=6)

        after = path.stat().st_size
        reports.append(f"  {path.name}: {before // 1024} KB -> {after // 1024} KB")
    return reports


def optimize_assets() -> list[str]:
    return optimize_raster_images(DIST_DIR / "assets" / IMAGES_DIR_NAME)

def build_page(env: Environment, page: dict) -> Path:
    template = env.get_template(page["template"])
    html = template.render(**page_context(page))
    output_path: Path = page["output"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def build() -> tuple[list[Path], list[str]]:
    if not TEMPLATES_DIR.is_dir():
        raise FileNotFoundError(f"Папка шаблонов не найдена: {TEMPLATES_DIR}")

    env = create_environment()
    copy_assets()
    image_reports = optimize_assets()
    outputs = [build_page(env, page) for page in PAGES]
    (DIST_DIR / ".nojekyll").touch()
    return outputs, image_reports


def main() -> int:
    try:
        outputs, image_reports = build()
    except Exception as exc:
        print(f"Ошибка сборки: {exc}", file=sys.stderr)
        return 1

    print("Сборка завершена:")
    for path in outputs:
        print(f"  -> {path.relative_to(ROOT)}")

    if image_reports:
        print("\nИзображения (Pillow):")
        for line in image_reports:
            print(line)
    else:
        print("\nИзображения: PNG/JPEG в assets/images/ не найдены — сжатие пропущено.")

    print("\nЛокальный просмотр:")
    print("  python -m http.server --directory dist")
    print("  RU: http://localhost:8000/")
    print("  EN: http://localhost:8000/en/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
