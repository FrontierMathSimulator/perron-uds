import unittest

import sympy as sp

from perron_uds.universal_divisor_saturation import (
    abelian_p_group_is_uds,
    unit_residue_profile,
    v4_cq_augmentation_three_fourier,
)
from run_mixed_abelian_uds_audit import group_elements, quotient_left_matrix


class UniversalDivisorSaturationTests(unittest.TestCase):
    def test_unit_residue_saturation_profiles(self):
        v4 = unit_residue_profile(4, (1, 3))
        c3_squared = unit_residue_profile(9, (1, 8))
        self.assertEqual(v4["residue_saturation_index"], 1)
        self.assertEqual(v4["relative_coprime_density"], 1)
        self.assertEqual(c3_squared["residue_saturation_index"], 3)
        self.assertEqual(c3_squared["relative_coprime_density"], sp.Rational(1, 3))

    def test_complete_abelian_p_group_classification(self):
        for factors in ((), (2,), (4,), (8,), (3,), (9,), (2, 2)):
            self.assertTrue(abelian_p_group_is_uds(factors))
        for factors in ((2, 2, 2), (2, 4), (4, 4), (3, 3), (5, 5), (5, 25)):
            self.assertFalse(abelian_p_group_is_uds(factors))

    def test_mixed_sylow_augmentation_three_fourier_factorization(self):
        audit = v4_cq_augmentation_three_fourier(5, 1, 2)
        self.assertEqual(
            tuple(channel["absolute_cyclotomic_norm"] for channel in audit["channels"]),
            (1, 11, 1, 11),
        )
        self.assertEqual(audit["quotient_lattice_determinant"], -121)
        self.assertFalse(audit["all_channels_are_units"])

        elements = group_elements((2, 2, 5))
        support = {(0, 0, 0), (1, 0, 1), (0, 1, 2)}
        coefficients = tuple(int(element in support) for element in elements)
        quotient_matrix = quotient_left_matrix(coefficients, (2, 2, 5))
        self.assertEqual(
            int(sp.Matrix(quotient_matrix).det(method="domain-ge")),
            audit["quotient_lattice_determinant"],
        )

    def test_signed_trinomial_theorem_named_controls(self):
        symmetric = v4_cq_augmentation_three_fourier(5, 2, 1)
        self.assertEqual(
            tuple(
                channel["absolute_cyclotomic_norm"]
                for channel in symmetric["channels"]
            ),
            (1, 1, 11, 11),
        )
        collision = v4_cq_augmentation_three_fourier(5, 0, 1)
        self.assertEqual(
            tuple(
                channel["absolute_cyclotomic_norm"]
                for channel in collision["channels"]
            ),
            (11, 31, 1, 1),
        )
        self.assertFalse(symmetric["all_channels_are_units"])
        self.assertFalse(collision["all_channels_are_units"])

    def test_validation(self):
        with self.assertRaisesRegex(ValueError, "multiplicatively closed"):
            unit_residue_profile(8, (1, 3, 5))
        with self.assertRaisesRegex(ValueError, "same underlying prime"):
            abelian_p_group_is_uds((2, 3))
        with self.assertRaisesRegex(ValueError, "other than 3"):
            v4_cq_augmentation_three_fourier(3, 0, 1)


if __name__ == "__main__":
    unittest.main()
