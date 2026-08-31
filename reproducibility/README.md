# Reproducibility guide

This directory is self-contained with respect to project-specific inputs. It
does not read the private upstream checkout, its working tree, or a sibling
paper repository.

## Environment

- Python 3.11 or newer
- Fully resolved dependency versions and hashes from the repository root
  `requirements.lock` (`requirements.txt` records the direct requirements)

Create an isolated environment from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --require-hashes -r requirements.lock
```

## One-command reproduction

```powershell
pwsh scripts/reproduce.ps1
```

or:

```bash
bash scripts/reproduce.sh
```

Both entry points run the focused paper tests, enumerate the exact
`C2 x C2 x C3` augmentation-five search, and compare the complete in-memory
result with the source-level constants in `expected_certificate.py`.

The standalone audit CLI may also be run from any working directory. Without
`--output`, it writes optional generated JSON to the ignored local path
`reproducibility/results/mixed_abelian_uds_c2_c2_c3_aug5.json`.

Expected terminal summary:

```text
Verified exact certificate: 4368 vectors, 0 units, digest bf2ddd8dda89583df964ef210cb67e637e626267f8058bfe0e2a8dc78b732c4f
```

Typical runtime is under a few seconds on a modern desktop. The calculation is
single-process and deterministic.

## What the certificate proves

For `G = C2 x C2 x C3`, the quotient

```text
A_G = Z[G] / Z*Omega
```

is represented as a free rank-eleven lattice by eliminating the identity
basis vector. A class is a unit exactly when its quotient multiplication
matrix has determinant `+1` or `-1`. There are `binomial(16,11) = 4368`
nonnegative coefficient vectors of augmentation five. The program checks all
of them and finds no unit.

The modular filters at 101, 103, and 107 are exact rejection tests. Exact
integer determinants are evaluated for candidates that survive all filters.
For the flagship case, no candidate survives.

## Certificate byte format

The certificate digest covers exactly 4,368 records in the order emitted by
`weak_compositions(5, 12)`: the first coefficient increases from zero through
five, and for each value the remaining coefficients are ordered by the same
recursive rule. The group basis is the lexicographically ordered Cartesian
product `range(2) x range(2) x range(3)`, so the last coordinate varies
fastest.

For each coefficient vector `(c0, ..., c11)`, serialize one record as follows:

1. Append the twelve coefficients as twelve raw unsigned bytes. Each
   coefficient is in the inclusive range 0 through 5; these are byte values,
   not ASCII digits, and there are no separators between them.
2. Append the literal ASCII vertical bar byte `0x7c`.
3. Append the canonical residues of the quotient determinant modulo 101, 103,
   and 107, in that order. Each residue is in `0 <= r < p` and is encoded as
   unpadded base-ten ASCII; separate the three fields with ASCII commas
   (`0x2c`).
4. Append one LF byte (`0x0a`), including after the final record. Do not append
   a CR byte, BOM, header, or any other data.

The reported SHA-256 value is computed over the concatenation of these 4,368
records.

## Symbolic versus computational claims

The all-prime signed-trinomial theorem in the paper is proved symbolically.
Tests over the primes 5, 7, 11, and 13 verify named and exhaustive finite
controls only; they are not evidence used to infer the theorem.
