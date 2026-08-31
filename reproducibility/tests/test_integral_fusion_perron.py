import unittest

from perron_uds.integral_fusion_perron import (
    coprime_residues,
    low_exponent_abelian_uplus_contains,
    regular_object_data,
    regular_quotient_factor,
    uds_counterexample_regular_shift,
)


class IntegralFusionPerronTests(unittest.TestCase):
    def test_regular_object_and_plus_minus_factors(self):
        # Integral dimensions of Rep(S3): 1, sign, and the standard object.
        self.assertEqual(regular_object_data((1, 1, 2))["global_dimension"], 6)

        plus = regular_quotient_factor((1, 1, 2), 7)
        minus = regular_quotient_factor((1, 1, 2), 5)
        self.assertEqual(plus["coefficients"], (2, 1, 2))
        self.assertEqual(plus["quotient_sign"], 1)
        self.assertEqual(minus["coefficients"], (0, 1, 2))
        self.assertEqual(minus["quotient_sign"], -1)

    def test_all_regular_factors_through_a_bounded_range(self):
        dimensions = (1, 1, 2)
        for value in range(1, 301):
            if value % 6 not in (1, 5):
                with self.assertRaises(ValueError):
                    regular_quotient_factor(dimensions, value)
                continue
            audit = regular_quotient_factor(dimensions, value)
            self.assertTrue(all(coefficient >= 0 for coefficient in audit["coefficients"]))

    def test_low_exponent_uplus_formulas(self):
        for order in (4, 8, 9):
            observed = tuple(
                value
                for value in range(1, 4 * order + 1)
                if low_exponent_abelian_uplus_contains(order, value)
            )
            expected = tuple(
                value
                for value in range(1, 4 * order + 1)
                if value % order in (1, order - 1)
            )
            self.assertEqual(observed, expected)

        self.assertEqual(coprime_residues(4), (1, 3))
        self.assertEqual(coprime_residues(9), (1, 2, 4, 5, 7, 8))
        self.assertTrue(
            all(
                low_exponent_abelian_uplus_contains(4, value)
                for value in range(1, 40, 2)
            )
        )
        self.assertFalse(low_exponent_abelian_uplus_contains(9, 2))
        self.assertFalse(low_exponent_abelian_uplus_contains(8, 3))

    def test_regular_shift_uds_counterexamples(self):
        self.assertEqual(
            uds_counterexample_regular_shift(9, 2),
            {"group_order": 9, "generator_dimension": 10, "missing_factor": 2},
        )
        self.assertEqual(
            uds_counterexample_regular_shift(8, 3),
            {"group_order": 8, "generator_dimension": 9, "missing_factor": 3},
        )

    def test_validation(self):
        with self.assertRaisesRegex(ValueError, "tensor-unit"):
            regular_object_data((2, 1))
        with self.assertRaisesRegex(ValueError, "must divide"):
            uds_counterexample_regular_shift(9, 3)


if __name__ == "__main__":
    unittest.main()
