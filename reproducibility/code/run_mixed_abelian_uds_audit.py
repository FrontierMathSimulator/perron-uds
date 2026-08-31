"""Exact low-augmentation quotient-unit audit for finite abelian group rings.

The quotient ``A_G = Z[G] / Z*Omega`` is represented by eliminating the
identity basis vector with the relation ``Omega = 0``.  For every positive
group-ring element of a prescribed augmentation, the script computes the
determinant of left multiplication on ``A_G``.  Its class is a unit exactly
when this determinant is ``+1`` or ``-1``.

The intended bounded flagship is ``G = C2 x C2 x C3`` at augmentation five:
there are only binomial(16, 11) = 4368 coefficient vectors.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from math import comb
from pathlib import Path

import sympy as sp


DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1]
    / "results"
    / "mixed_abelian_uds_c2_c2_c3_aug5.json"
)


def group_elements(moduli: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.product(*(range(n) for n in moduli)))


def weak_compositions(total: int, parts: int):
    """Yield all ``parts``-tuples of nonnegative integers summing to total."""

    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in weak_compositions(total - first, parts - 1):
            yield (first,) + tail


def quotient_left_matrix(
    coefficients: tuple[int, ...], moduli: tuple[int, ...]
) -> list[list[int]]:
    elements = group_elements(moduli)
    positions = {element: i for i, element in enumerate(elements)}
    rank = len(elements) - 1
    matrix = [[0] * rank for _ in range(rank)]

    for column, right in enumerate(elements[1:]):
        product = [0] * len(elements)
        for left, coefficient in zip(elements, coefficients):
            target = tuple((a + b) % n for a, b, n in zip(left, right, moduli))
            product[positions[target]] += coefficient
        identity_coefficient = product[0]
        for row in range(rank):
            matrix[row][column] = product[row + 1] - identity_coefficient
    return matrix


def determinant_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    determinant = 1
    size = len(work)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column]
        determinant = determinant * pivot_value % prime
        inverse = pow(pivot_value, -1, prime)
        for row in range(column + 1, size):
            factor = work[row][column] * inverse % prime
            if factor:
                for j in range(column, size):
                    work[row][j] = (work[row][j] - factor * work[column][j]) % prime
    return determinant % prime


def audit(moduli: tuple[int, ...], augmentation: int) -> dict[str, object]:
    order = 1
    for modulus in moduli:
        order *= modulus
    expected = comb(augmentation + order - 1, order - 1)
    modular_primes = (101, 103, 107)
    exact_histogram: dict[str, int] = {}
    units: list[tuple[int, ...]] = []
    digest = hashlib.sha256()
    modular_survivors = 0
    per_prime_pm_one_counts = {str(prime): 0 for prime in modular_primes}
    checked = 0

    for coefficients in weak_compositions(augmentation, order):
        matrix = quotient_left_matrix(coefficients, moduli)
        residues = tuple(determinant_mod(matrix, prime) for prime in modular_primes)
        digest.update(bytes(coefficients))
        digest.update(b"|")
        digest.update(",".join(map(str, residues)).encode("ascii"))
        digest.update(b"\n")
        checked += 1
        for residue, prime in zip(residues, modular_primes):
            if residue in (1, prime - 1):
                per_prime_pm_one_counts[str(prime)] += 1
        if not all(residue in (1, prime - 1) for residue, prime in zip(residues, modular_primes)):
            continue
        signs = tuple(1 if residue == 1 else -1 for residue, prime in zip(residues, modular_primes))
        if len(set(signs)) != 1:
            continue
        modular_survivors += 1
        determinant = int(sp.Matrix(matrix).det(method="domain-ge"))
        exact_histogram[str(determinant)] = exact_histogram.get(str(determinant), 0) + 1
        if abs(determinant) == 1:
            units.append(coefficients)

    assert checked == expected
    return {
        "group_moduli": list(moduli),
        "group_order": order,
        "augmentation": augmentation,
        "positive_vectors_checked": checked,
        "expected_positive_vectors": expected,
        "modular_primes": list(modular_primes),
        "per_prime_pm_one_counts": per_prime_pm_one_counts,
        "modular_survivors": modular_survivors,
        "exact_survivor_determinant_histogram": exact_histogram,
        "unit_count": len(units),
        "unit_vectors": [list(vector) for vector in units],
        "enumeration_residue_sha256": digest.hexdigest(),
        "claim": (
            "EXACT COMPUTATIONAL CERTIFICATE: exhaustive positive coefficient "
            "enumeration; quotient-unit membership is det = +/-1."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moduli", nargs="+", type=int, default=[2, 2, 3])
    parser.add_argument("--augmentation", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    args = parser.parse_args()
    result = audit(tuple(args.moduli), args.augmentation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
