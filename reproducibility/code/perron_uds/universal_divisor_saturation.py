"""Exact finite checks used by the structural UDS classification."""

from __future__ import annotations

from math import gcd
from typing import Sequence

import sympy as sp


def unit_residue_profile(modulus: int, residues: Sequence[int]) -> dict[str, object]:
    """Validate a subgroup of ``(Z/modulus)^x`` and report its saturation index."""

    if modulus < 2:
        raise ValueError("modulus must be at least 2")
    subgroup = tuple(sorted({int(value) % modulus for value in residues}))
    if 1 not in subgroup or any(gcd(value, modulus) != 1 for value in subgroup):
        raise ValueError("residues must contain 1 and be units modulo the modulus")
    if any((left * right) % modulus not in subgroup for left in subgroup for right in subgroup):
        raise ValueError("residues must be multiplicatively closed")
    if any(
        not any((value * inverse) % modulus == 1 for inverse in subgroup)
        for value in subgroup
    ):
        raise ValueError("residues must contain multiplicative inverses")
    phi = int(sp.totient(modulus))
    if phi % len(subgroup):
        raise AssertionError("subgroup order must divide Euler's totient")
    return {
        "modulus": modulus,
        "unit_residues": subgroup,
        "residue_saturation_index": phi // len(subgroup),
        "natural_density": sp.Rational(len(subgroup), modulus),
        "relative_coprime_density": sp.Rational(len(subgroup), phi),
    }


def abelian_p_group_is_uds(invariant_factors: Sequence[int]) -> bool:
    """Apply the proved abelian p-group UDS classification.

    ``invariant_factors`` lists the nontrivial cyclic prime-power factors.
    The answer is true exactly for cyclic groups and ``C2 x C2`` (and for the
    trivial group, represented by an empty tuple).
    """

    factors = tuple(int(value) for value in invariant_factors)
    if not factors:
        return True
    if any(value < 2 or len(sp.factorint(value)) != 1 for value in factors):
        raise ValueError("factors must be nontrivial prime powers")
    primes = {int(next(iter(sp.factorint(value)))) for value in factors}
    if len(primes) != 1:
        raise ValueError("all factors must have the same underlying prime")
    return len(factors) == 1 or factors == (2, 2)


def v4_cq_augmentation_three_fourier(
    prime: int, first_exponent: int, second_exponent: int
) -> dict[str, object]:
    """Audit the four cyclotomic channels of the mixed-Sylow test letter.

    After the exact ``V4`` row-profile reduction, every positive
    augmentation-three quotient-unit candidate on ``V4 x C_q`` is, up to a
    group-element translate,

    ``1 + e1*t**r + e2*t**s``.

    The four returned resultants are the absolute cyclotomic norms of
    ``1 +/- zeta_q**r +/- zeta_q**s``.  All four must equal one for the class
    to be a unit in ``Z[V4 x C_q] / Z*Omega``.  This routine checks one named
    candidate; it is not a prime or coefficient census.
    """

    q = int(prime)
    if not sp.isprime(q) or q in (2, 3):
        raise ValueError("prime must be an odd prime other than 3")
    r = int(first_exponent) % q
    s = int(second_exponent) % q
    variable = sp.symbols("T")
    cyclotomic = sp.cyclotomic_poly(q, variable)
    channels: list[dict[str, object]] = []
    norm_product = 1
    for first_sign in (1, -1):
        for second_sign in (1, -1):
            polynomial = 1 + first_sign * variable**r + second_sign * variable**s
            norm = abs(int(sp.resultant(cyclotomic, polynomial, variable)))
            norm_product *= norm
            channels.append(
                {
                    "signs": (first_sign, second_sign),
                    "polynomial": str(sp.expand(polynomial)),
                    "absolute_cyclotomic_norm": norm,
                }
            )
    return {
        "prime": q,
        "normalized_exponents": (r, s),
        "channels": tuple(channels),
        "all_channels_are_units": all(
            channel["absolute_cyclotomic_norm"] == 1 for channel in channels
        ),
        # The three nontrivial V4 characters at t=1 have product -1 for the
        # normalized support {0,e1,e2}.
        "quotient_lattice_determinant": -norm_product,
    }
