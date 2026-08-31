"""Finalize identity-neutral publication metadata and the Pages package."""

from __future__ import annotations

from html import escape
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MANUSCRIPT = ROOT / "paper" / "manuscript.qmd"
URL_TOKEN = "__PUBLICATION_URL__"
PDF_URL_TOKEN = "__PUBLICATION_PDF_URL__"


def publication_url() -> str:
    configured = os.environ.get("PUBLICATION_URL", "").strip()
    if not configured and os.environ.get("REQUIRE_PUBLICATION_URL") == "1":
        raise RuntimeError(
            "PUBLICATION_URL must be configured for a public deployment"
        )
    value = configured or "http://localhost:8000/"
    if not value.endswith("/"):
        value += "/"
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("PUBLICATION_URL must be an absolute HTTP(S) URL")
    return value


def manuscript_date() -> str:
    source = MANUSCRIPT.read_text(encoding="utf-8")
    match = re.search(r"^date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", source, re.MULTILINE)
    if match is None:
        raise ValueError("canonical manuscript date is missing")
    return match.group(1)


def copy_public_reproducibility_package() -> None:
    target = DOCS / "reproducibility"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    source = ROOT / "reproducibility"
    for filename in ("README.md", "reproduce.py", "expected_certificate.py"):
        shutil.copy2(source / filename, target / filename)
    for dirname in ("code", "tests"):
        shutil.copytree(
            source / dirname,
            target / dirname,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )

    shutil.copy2(ROOT / "requirements.txt", DOCS / "requirements.txt")
    shutil.copy2(ROOT / "requirements.lock", DOCS / "requirements.lock")
    shutil.copytree(ROOT / "paper" / "fonts", DOCS / "fonts", dirs_exist_ok=True)
    shutil.copy2(ROOT / "LICENSE", DOCS / "LICENSE")
    shutil.copy2(ROOT / "CITATION.cff", DOCS / "CITATION.cff")
    scripts = DOCS / "scripts"
    scripts.mkdir(exist_ok=True)
    for filename in ("reproduce.ps1", "reproduce.sh"):
        shutil.copy2(ROOT / "scripts" / filename, scripts / filename)


def main() -> int:
    base_url = publication_url()
    pdf_url = urljoin(base_url, "paper.pdf")
    index = DOCS / "index.html"
    html = index.read_text(encoding="utf-8")
    if URL_TOKEN not in html or PDF_URL_TOKEN not in html:
        raise ValueError("publication URL placeholders are missing from generated HTML")
    html = html.replace(PDF_URL_TOKEN, pdf_url).replace(URL_TOKEN, base_url)
    if URL_TOKEN in html or PDF_URL_TOKEN in html:
        raise AssertionError("publication URL placeholder remains")
    index.write_text(html, encoding="utf-8", newline="\n")

    modified = manuscript_date()
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{escape(base_url)}</loc>
    <lastmod>{modified}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{escape(pdf_url)}</loc>
    <lastmod>{modified}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
"""
    (DOCS / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    (DOCS / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {urljoin(base_url, 'sitemap.xml')}\n",
        encoding="utf-8",
        newline="\n",
    )
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    copy_public_reproducibility_package()
    intermediate = DOCS / "paper"
    if intermediate.exists():
        shutil.rmtree(intermediate)
    print(f"Finalized publication metadata for {base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
