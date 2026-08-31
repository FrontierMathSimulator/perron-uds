"""Exact arithmetic checks used by the Perron-UDS paper."""

from __future__ import annotations

from math import gcd
from typing import Sequence


def regular_object_data(simple_dimensions: Sequence[int]) -> dict[str, object]:
    """Return the integral regular vector and global dimension."""

    dimensions = tuple(int(value) for value in simple_dimensions)
    if not dimensions or dimensions[0] != 1:
        raise ValueError("the tensor-unit dimension must be the first entry and equal 1")
    if any(value < 1 for value in dimensions):
        raise ValueError("simple dimensions must be positive integers")
    return {
        "simple_dimensions": dimensions,
        "regular_coefficients": dimensions,
        "global_dimension": sum(value * value for value in dimensions),
    }


def regular_quotient_factor(
    simple_dimensions: Sequence[int], dimension: int
) -> dict[str, object]:
    """Construct the ``+1`` or ``-1`` regular-line factor of given dimension.

    The construction applies exactly when ``dimension`` is congruent to
    ``+1`` or ``-1`` modulo the global dimension.  If both descriptions are
    possible (only a degenerate small modulus issue), the plus form is used.
    """

    data = regular_object_data(simple_dimensions)
    dims = data["simple_dimensions"]
    global_dimension = int(data["global_dimension"])
    if dimension < 1:
        raise ValueError("dimension must be positive")

    if (dimension - 1) % global_dimension == 0:
        sign = 1
        multiplier = (dimension - 1) // global_dimension
        coefficients = tuple(
            multiplier * value + (index == 0)
            for index, value in enumerate(dims)
        )
    elif (dimension + 1) % global_dimension == 0:
        sign = -1
        multiplier = (dimension + 1) // global_dimension
        coefficients = tuple(
            multiplier * value - (index == 0)
            for index, value in enumerate(dims)
        )
    else:
        raise ValueError("dimension must be congruent to +1 or -1 modulo D")

    if any(value < 0 for value in coefficients):
        raise AssertionError("the regular quotient factor is not positive")
    if sum(value * dim for value, dim in zip(coefficients, dims, strict=True)) != dimension:
        raise AssertionError("dimension identity failed")
    return {
        **data,
        "dimension": int(dimension),
        "quotient_sign": sign,
        "regular_multiplier": multiplier,
        "coefficients": coefficients,
    }


def low_exponent_abelian_uplus_contains(group_order: int, dimension: int) -> bool:
    """Membership in the proved low-exponent abelian ``U_+`` formula.

    This applies to finite abelian groups whose exponent divides 2, 3, 4, or
    6.  The group exponent is a theorem-side hypothesis and is intentionally
    not inferred from the order alone.
    """

    if group_order < 1 or dimension < 1:
        raise ValueError("group_order and dimension must be positive")
    return dimension % group_order in {1 % group_order, (-1) % group_order}


def uds_counterexample_regular_shift(group_order: int, missing_factor: int) -> dict[str, int]:
    """Audit the standard ``x=1+R_G`` obstruction to UDS.

    The caller must separately prove that ``missing_factor`` is absent from
    ``U_+(G)``.  This function checks only the smoothness arithmetic.
    """

    if group_order < 2 or missing_factor < 2:
        raise ValueError("group_order and missing_factor must be at least 2")
    generator_dimension = group_order + 1
    if generator_dimension % missing_factor:
        raise ValueError("missing_factor must divide |G|+1")
    return {
        "group_order": int(group_order),
        "generator_dimension": generator_dimension,
        "missing_factor": int(missing_factor),
    }


def coprime_residues(modulus: int) -> tuple[int, ...]:
    """Positive residue representatives coprime to ``modulus``."""

    if modulus < 1:
        raise ValueError("modulus must be positive")
    return tuple(value for value in range(modulus) if gcd(value, modulus) == 1)
