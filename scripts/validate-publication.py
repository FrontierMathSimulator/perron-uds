"""Validate the generated web and PDF publication artifacts."""

from __future__ import annotations

from datetime import date
from html.parser import HTMLParser
import hashlib
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

from cffconvert import Citation
from jsonschema.exceptions import ValidationError as CffValidationError
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
HTML = DOCS / "index.html"
PDF = ROOT / "paper" / "main.pdf"
PUBLIC_PDF = DOCS / "paper.pdf"


class PublicationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: list[dict[str, str]] = []
        self.links: list[str] = []
        self.assets: list[str] = []
        self.ids: set[str] = set()
        self.headings: list[str] = []
        self._heading: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag == "meta":
            self.meta.append(values)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "link" and values.get("href"):
            self.assets.append(values["href"])
        if tag == "script" and values.get("src"):
            self.assets.append(values["src"])
        if values.get("id"):
            self.ids.add(values["id"])
        if tag in {"h1", "h2", "h3", "h4"}:
            self._heading = []

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4"} and self._heading is not None:
            self.headings.append(" ".join(self._heading).strip())
            self._heading = None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_fonts(reader: PdfReader) -> list[tuple[str, bool]]:
    """Return PDF base-font names and whether their programs are embedded."""

    found: list[tuple[str, bool]] = []
    for page in reader.pages:
        resources_ref = page.get("/Resources")
        if resources_ref is None:
            continue
        resources = resources_ref.get_object()
        fonts_ref = resources.get("/Font")
        if fonts_ref is None:
            continue
        for font_ref in fonts_ref.get_object().values():
            top_font = font_ref.get_object()
            candidates = [top_font]
            descendants_ref = top_font.get("/DescendantFonts")
            if descendants_ref is not None:
                candidates.extend(
                    item.get_object() for item in descendants_ref.get_object()
                )
            for font in candidates:
                name = str(font.get("/BaseFont", ""))
                if not name:
                    continue
                descriptor_ref = font.get("/FontDescriptor")
                embedded = False
                if descriptor_ref is not None:
                    descriptor = descriptor_ref.get_object()
                    embedded = any(
                        descriptor.get(key) is not None
                        for key in ("/FontFile", "/FontFile2", "/FontFile3")
                    )
                found.append((name, embedded))
    return found


def main() -> int:
    require(HTML.is_file(), "docs/index.html is missing")
    require(PDF.is_file(), "paper/main.pdf is missing")
    require(PUBLIC_PDF.is_file(), "docs/paper.pdf is missing")
    require((DOCS / "sitemap.xml").is_file(), "docs/sitemap.xml is missing")
    require((DOCS / "requirements.lock").is_file(), "public dependency lock is missing")
    for font_file in ("Gelasio-Roman-VF.ttf", "Gelasio-Italic-VF.ttf", "OFL.txt"):
        require((DOCS / "fonts" / font_file).is_file(), f"public font asset is missing: {font_file}")
    require(sha256(PDF) == sha256(PUBLIC_PDF), "public and formal PDFs differ")

    html = HTML.read_text(encoding="utf-8")
    manuscript = (ROOT / "paper" / "manuscript.qmd").read_text(encoding="utf-8")
    stylesheet = (ROOT / "paper" / "paper.css").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    try:
        Citation(citation, src="CITATION.cff").validate()
    except (CffValidationError, ValueError) as error:
        raise AssertionError(f"CITATION.cff fails the CFF 1.2 schema: {error}") from error
    require(
        re.search(r"^type:\s*software\s*$", citation, re.MULTILINE) is not None,
        "CFF root must describe the repository package as software",
    )
    require(
        re.search(r"^preferred-citation:\s*$", citation, re.MULTILINE) is not None,
        "CFF preferred article citation is missing",
    )
    author_match = re.search(r'^author:\s*["\']?([^"\'\r\n]+)', manuscript, re.MULTILINE)
    require(author_match is not None, "canonical manuscript author is missing")
    expected_author = author_match.group(1).strip()
    date_match = re.search(r"^date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", manuscript, re.MULTILINE)
    require(date_match is not None, "canonical manuscript date is missing")
    expected_date = date.fromisoformat(date_match.group(1)).isoformat()
    cff_given = re.search(r'^\s*(?:-\s*)?given-names:\s*"([^"]+)"', citation, re.MULTILINE)
    cff_family = re.search(r'^\s*family-names:\s*"([^"]+)"', citation, re.MULTILINE)
    require(cff_given is not None and cff_family is not None, "CFF author is missing")
    require(
        f"{cff_given.group(1)} {cff_family.group(1)}" == expected_author,
        "CFF and manuscript authors differ",
    )
    for required_rule in {
        "docs/",
        "paper/main.pdf",
        "paper/main.typ",
        "paper/manuscript.typ",
        "reproducibility/results/",
    }:
        require(required_rule in gitignore.splitlines(), f"missing ignore rule: {required_rule}")
    require("license: CC0 1.0 Universal" in manuscript, "manuscript CC0 metadata missing")
    require("license: CC0-1.0" in citation, "CFF CC0 metadata missing")
    require(
        f"date-released: {expected_date}" in citation,
        "CFF release date differs from the manuscript date",
    )
    require("CC0 1.0 Universal" in license_text, "CC0 license notice missing")
    for legal_heading in {"Statement of Purpose", "3. Public License Fallback", "4. Limitations and Disclaimers"}:
        require(legal_heading in license_text, f"canonical CC0 section missing: {legal_heading}")
    require(
        (ROOT / "THIRD_PARTY_NOTICES.md").is_file(),
        "third-party citation-style notice is missing",
    )
    require(
        re.search(r"\.proof::before\s*\{[^}]*content:\s*none", stylesheet, re.DOTALL)
        is not None,
        "stylesheet does not suppress the theme's duplicate proof label",
    )
    require("\\tag{" not in manuscript, "manual equation tags are forbidden")
    require(
        not re.search(r"\bEquations?\s+\d+\.\d+", manuscript),
        "hard-coded equation reference remains in manuscript",
    )
    require(
        not re.search(r"(?<!\\)\bqquad\b", manuscript),
        "malformed qquad command remains in manuscript",
    )
    require('G{\"o}' not in manuscript, "corrupted Görentaş spelling remains")
    require("Görentaş studies" in manuscript, "correct Görentaş attribution missing")
    for citation_key in {
        "@BovdiParmenter1997",
        "@Sehgal1993",
        "@KitaniSano2021",
        "@HernandezMeloEtAl2025",
    }:
        require(citation_key in manuscript, f"required prior-work citation missing: {citation_key}")
    require(
        "The unitary-unit classification in Theorem 9.1 is not claimed as new."
        in manuscript,
        "classical status of Theorem 9.1 is not explicit",
    )
    require(
        "rigorous repair and refinement" in manuscript,
        "Theorem 9.2 is not framed as a repair and refinement",
    )
    require(
        "supplies an independent correction" not in manuscript,
        "misleading independence claim remains",
    )
    require("If $n=1$" in manuscript, "trivial cyclic-group case is not explicit")
    require(
        "If $Q$ is trivial" in manuscript,
        "trivial quotient-group case is not explicit",
    )
    require(
        "Theorem 2.2 (arithmetic-tail normal form)" in manuscript,
        "arithmetic-tail theorem is missing",
    )
    require(
        "residue-saturation index" in manuscript,
        "residue-saturation index is missing",
    )
    require(
        "Theorem 5.3 (exact extractor orbit)" in manuscript,
        "exact extractor-orbit theorem is missing",
    )
    for required_label in {
        "eq-unit-residue-subgroup",
        "eq-arithmetic-tails",
        "eq-extractor-orbit",
    }:
        require(
            f"{{#{required_label}}}" in manuscript,
            f"required theorem equation is missing: {required_label}",
        )
    require(
        "a necessary general replacement for the sufficient nilpotent-kernel criterion"
        not in manuscript,
        "stale nilpotent-kernel open problem remains",
    )
    require(
        "a structural description of $U_+(K)$ for wider classes" not in manuscript,
        "stale U_+(K) structural open problem remains",
    )
    require("__PUBLICATION_" not in html, "publication URL placeholder remains")
    parser = PublicationParser()
    parser.feed(html)
    equation_labels = set(re.findall(r"\{#(eq-[a-z0-9-]+)\}", manuscript))
    require(len(equation_labels) >= 40, "too few labeled equations")
    for label in sorted(equation_labels):
        require(label in parser.ids, f"generated equation anchor missing: {label}")
    require("@eq-" not in html, "unresolved equation cross-reference in HTML")
    require("Görentaş studies" in html, "correct attribution missing from HTML")
    require(
        "not claimed as new" in html,
        "classical status of the unitary-unit theorem is missing from HTML",
    )
    require(
        "rigorous repair and refinement" in html,
        "trinomial theorem repair framing is missing from HTML",
    )
    require(
        "arithmetic-tail normal form" in html,
        "arithmetic-tail theorem missing from HTML",
    )
    require(
        "exact extractor orbit" in html,
        "extractor-orbit theorem missing from HTML",
    )
    require("<main" in html, "semantic main element missing")
    require(len(parser.headings) >= 20, "paper has too few semantic headings")
    require("sec-introduction" in parser.ids, "stable introduction anchor missing")
    require("refs" in parser.ids, "stable references anchor missing")
    require("Abstract" in html, "visible abstract heading missing")
    require(
        "finite abelian group" in html and "cyclic" in html,
        "main classification is missing from HTML",
    )

    def metas(key: str, value: str) -> list[dict[str, str]]:
        return [item for item in parser.meta if item.get(key) == value]

    require(metas("name", "description"), "meta description missing")
    require(metas("property", "og:title"), "Open Graph title missing")
    require(
        'class="quarto-title-meta-heading">Author' in html,
        "visible HTML author block is missing",
    )
    require(expected_author in html, "visible HTML author is incorrect")
    require(metas("name", "citation_title"), "citation_title missing")
    citation_authors = metas("name", "citation_author")
    require(citation_authors, "citation_author missing")
    require(
        any(item.get("content") == expected_author for item in citation_authors),
        "citation_author is incorrect",
    )
    require(
        metas("name", "citation_publication_date"),
        "citation_publication_date missing",
    )
    require(
        any(
            item.get("content") == expected_date
            for item in metas("name", "citation_publication_date")
        ),
        "citation_publication_date differs from the manuscript date",
    )
    require(metas("name", "citation_pdf_url"), "citation_pdf_url missing")
    require('"@type": "ScholarlyArticle"' in html, "ScholarlyArticle JSON-LD missing")
    require(
        f'"author": [{{"@type": "Person", "name": "{expected_author}"}}]' in html,
        "ScholarlyArticle author is incorrect",
    )
    require(
        f'"datePublished": "{expected_date}"' in html,
        "ScholarlyArticle publication date differs from the manuscript date",
    )
    require(
        '"license": "https://creativecommons.org/publicdomain/zero/1.0/"' in html,
        "ScholarlyArticle CC0 metadata is incorrect",
    )
    require('rel="canonical"' in html, "canonical link missing")

    for href in parser.links:
        parsed = urlparse(href)
        if parsed.scheme or href.startswith(("#", "mailto:")):
            continue
        target = unquote(parsed.path)
        if not target:
            continue
        candidate = (DOCS / target).resolve()
        require(candidate.exists(), f"broken local HTML link: {href}")

    for asset in parser.assets:
        parsed = urlparse(asset)
        if parsed.scheme or asset.startswith("data:"):
            continue
        target = unquote(parsed.path)
        if not target:
            continue
        candidate = (DOCS / target).resolve()
        require(candidate.exists(), f"missing local HTML asset: {asset}")

    reader = PdfReader(str(PDF))
    require(len(reader.pages) >= 15, "PDF is unexpectedly short")
    fonts = pdf_fonts(reader)
    require(
        any("Gelasio" in name and embedded for name, embedded in fonts),
        "PDF does not contain an embedded Gelasio text font",
    )
    require(
        not any("Georgia" in name or "DejaVuSerif" in name for name, _ in fonts),
        "PDF contains a substituted Georgia or DejaVu Serif text font",
    )
    metadata = reader.metadata or {}
    title = str(metadata.get("/Title", ""))
    require("Perron Divisibility" in title, "PDF title metadata is missing")
    author = str(metadata.get("/Author", "")).strip()
    require(author == expected_author, "PDF author metadata is incorrect")
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized = re.sub(r"\s+", " ", text)
    require(len(normalized) >= 30000, "PDF searchable text is unexpectedly short")
    require("finite-abelian UDS classification" in normalized, "PDF main theorem missing")
    require(
        "arithmetic-tail normal form" in normalized,
        "PDF arithmetic-tail theorem missing",
    )
    require(
        "exact extractor orbit" in normalized,
        "PDF extractor-orbit theorem missing",
    )
    require(
        "not claimed as new" in normalized,
        "PDF omits the classical status of the unitary-unit theorem",
    )
    require(
        "rigorous repair and refinement" in normalized,
        "PDF omits the trinomial theorem repair framing",
    )
    require(
        "References" in normalized or "Bibliography" in normalized,
        "PDF bibliography missing",
    )

    print(
        f"Validated {len(reader.pages)} PDF pages, {len(normalized)} searchable "
        f"characters, {len(parser.headings)} HTML headings, and required metadata."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"publication validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
