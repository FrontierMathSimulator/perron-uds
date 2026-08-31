# Focused regression tests

These tests exercise the exact computational certificate, the integral-fusion
Perron interfaces, the universal-divisor-saturation formulas, and the claims
that connect the reproducibility package to the manuscript.

Run the complete focused suite from the repository root with:

```text
python -m unittest discover -s reproducibility/tests -p "test_*.py"
```

The test modules are:

- `test_integral_fusion_perron.py`: regular-object, quotient-factor, and
  low-exponent checks.
- `test_mixed_abelian_uds_audit.py`: exact and modular determinant checks for
  the finite mixed-abelian certificate.
- `test_universal_divisor_saturation.py`: residue-profile, finite abelian
  p-group, and Fourier-channel checks.
- `test_whitepaper_claims.py`: source-level certificate expectations and
  manuscript-facing regression controls.

These tests are regression controls. They do not replace the symbolic proofs
in the paper and do not extrapolate the finite certificate to larger primes.
