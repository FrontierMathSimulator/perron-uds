"""Source-level reference values for the exact q=3 certificate."""

EXPECTED_Q3_CERTIFICATE: dict[str, object] = {
    "group_moduli": [2, 2, 3],
    "group_order": 12,
    "augmentation": 5,
    "positive_vectors_checked": 4368,
    "expected_positive_vectors": 4368,
    "modular_primes": [101, 103, 107],
    "per_prime_pm_one_counts": {"101": 144, "103": 72, "107": 0},
    "modular_survivors": 0,
    "exact_survivor_determinant_histogram": {},
    "unit_count": 0,
    "unit_vectors": [],
    "enumeration_residue_sha256": (
        "bf2ddd8dda89583df964ef210cb67e637e626267f8058bfe0e2a8dc78b732c4f"
    ),
    "claim": (
        "EXACT COMPUTATIONAL CERTIFICATE: exhaustive positive coefficient "
        "enumeration; quotient-unit membership is det = +/-1."
    ),
}
