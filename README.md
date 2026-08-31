# Perron divisibility and universal divisor saturation

> **Main theorem.** For a finite abelian group `G`, the integral group ring
> `Z[G]` has universal divisor saturation exactly when `G` is cyclic or
> `G = C2 x C2`.

This repository contains a complete, reproducible whitepaper draft about
positive divisors of powers in integral fusion based rings. The general engine
is a Perron lifting theorem: a positive unit modulo the regular line divides
all sufficiently large admissible powers of every primitive positive input.

**Read first:** [canonical paper source](paper/manuscript.qmd) ·
[reproducibility guide](reproducibility/README.md)

The build creates the full HTML, PDF, and Markdown editions locally under
`docs/` and `paper/main.pdf`. These generated artifacts are intentionally
ignored; the Pages workflow rebuilds them for publication.

Before enabling Pages deployment, configure the repository variable
`PUBLICATION_URL` with the final absolute site URL. Local builds use
`http://localhost:8000/` for metadata and sitemap validation.

## What is proved

- The regular element is central and supports the quotient
  `A_K = K / Z Omega` for every integral fusion based ring.
- Positive quotient units lift to genuine positive divisors through the
  correct right-multiplication Perron limit.
- Every primitive element of `N[C_n]` has positive divisors of exactly all
  smooth augmentations.
- UDS descends along finite-group quotients.
- A finite abelian `p`-group is UDS exactly when it is cyclic or `C2 x C2`.
- For primes `q >= 5`, a symbolic signed-trinomial theorem rules out the four
  simultaneous cyclotomic units required by `C2^2 x C_q`.
- For `q = 3`, an exact exhaustive certificate checks all 4,368 positive
  augmentation-five vectors and finds no quotient unit.

The all-prime theorem is symbolic. Finite-prime calculations are regression
controls only.

## Fast reproduction

Python 3.11 or newer is required. Quarto 1.10.18 is required only to rebuild
the publication artifacts; Quarto includes the Typst PDF engine.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --require-hashes -r requirements.lock
pwsh scripts/reproduce.ps1
pwsh scripts/build-paper.ps1
```

On Linux or macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
bash scripts/reproduce.sh
bash scripts/build-paper.sh
```

The exact certificate must report:

```text
4368 vectors, 0 units
bf2ddd8dda89583df964ef210cb67e637e626267f8058bfe0e2a8dc78b732c4f
```

## Repository map

| Path | Purpose |
|---|---|
| `paper/manuscript.qmd` | Single authoritative manuscript source |
| `paper/references.bib` | Conventional scholarly bibliography |
| `paper/fonts/` | Bundled OFL-licensed Gelasio fonts used by PDF and HTML |
| `paper/main.pdf` | Generated searchable formal edition (ignored) |
| `docs/` | Generated HTML, PDF, Markdown, and Pages package (ignored) |
| `reproducibility/code/perron_uds/` | Project-specific computational modules |
| `reproducibility/tests/` | Focused and whitepaper-specific regression tests |
| `reproducibility/expected_certificate.py` | Source-level certificate expectations |
| `reproducibility/results/` | Optional generated JSON output (ignored) |
| `scripts/` | Cross-platform build and reproduction entry points |
| `requirements.lock` | Fully resolved, hash-checked Python environment |
| `.github/workflows/` | CI and GitHub Pages deployment |

## Claim boundaries

This paper does **not** classify UDS for all nonabelian finite groups. UDS is a
dimensioned based-semiring property; it is not claimed to be Morita invariant,
is not stable under tensor products, and is not a synonym for the numerical
index image of one chain. Rational/Wedderburn invertibility is not promoted to
integral quotient-unit membership. The modular nilpotence criterion is
sufficient, not generally necessary.

## Citation

This is a publication-oriented preprint draft, not a claim of peer review or
priority. Citation metadata is provided in [CITATION.cff](CITATION.cff).

## License

Original manuscript, software, data, and documentation are dedicated under
CC0 1.0 Universal. The vendored citation style retains its CC BY-SA 3.0
license. See [LICENSE](LICENSE) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
