from pathlib import Path
import unittest

from expected_certificate import EXPECTED_Q3_CERTIFICATE
from run_mixed_abelian_uds_audit import DEFAULT_OUTPUT
from perron_uds.universal_divisor_saturation import (
    v4_cq_augmentation_three_fourier,
)


class WhitepaperClaimRegressionTests(unittest.TestCase):
    def test_certificate_cli_default_is_repository_local(self):
        expected = (
            Path(__file__).resolve().parents[1]
            / "results"
            / "mixed_abelian_uds_c2_c2_c3_aug5.json"
        )
        self.assertEqual(DEFAULT_OUTPUT, expected)

    def test_certificate_expectations_are_source_level(self):
        self.assertEqual(EXPECTED_Q3_CERTIFICATE["positive_vectors_checked"], 4368)
        self.assertEqual(EXPECTED_Q3_CERTIFICATE["unit_count"], 0)
        self.assertEqual(EXPECTED_Q3_CERTIFICATE["modular_survivors"], 0)

    def test_signed_trinomial_norm_one_patterns(self):
        """Finite-prime regression only; the paper supplies the all-prime proof."""

        for prime in (5, 7, 11, 13):
            for r in range(prime):
                for s in range(prime):
                    audit = v4_cq_augmentation_three_fourier(prime, r, s)
                    mixed_norm = next(
                        channel["absolute_cyclotomic_norm"]
                        for channel in audit["channels"]
                        if channel["signs"] == (1, -1)
                    )
                    expected = s == 0 or s == r or r == (2 * s) % prime
                    self.assertEqual(
                        mixed_norm == 1,
                        expected,
                        msg=f"q={prime}, r={r}, s={s}, norm={mixed_norm}",
                    )

    def test_no_four_channel_candidate_in_regression_primes(self):
        for prime in (5, 7, 11, 13):
            for r in range(prime):
                for s in range(prime):
                    audit = v4_cq_augmentation_three_fourier(prime, r, s)
                    self.assertFalse(
                        audit["all_channels_are_units"],
                        msg=f"unexpected candidate q={prime}, r={r}, s={s}",
                    )


if __name__ == "__main__":
    unittest.main()
