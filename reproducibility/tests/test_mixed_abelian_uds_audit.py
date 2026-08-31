import unittest

import sympy as sp

from run_mixed_abelian_uds_audit import (
    audit,
    determinant_mod,
    quotient_left_matrix,
)


class MixedAbelianUdsAuditTests(unittest.TestCase):
    def test_identity_acts_as_identity_on_regular_quotient(self):
        matrix = quotient_left_matrix((1,) + (0,) * 11, (2, 2, 3))
        self.assertEqual(matrix, [[int(i == j) for j in range(11)] for i in range(11)])

    def test_modular_determinant_matches_exact_representatives(self):
        representatives = (
            (5,) + (0,) * 11,
            (1, 1, 1, 1, 1) + (0,) * 7,
            (0, 2, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0),
        )
        for coefficients in representatives:
            matrix = quotient_left_matrix(coefficients, (2, 2, 3))
            exact = int(sp.Matrix(matrix).det(method="domain-ge"))
            self.assertEqual(determinant_mod(matrix, 107), exact % 107)

    def test_c2_c2_c3_has_no_positive_augmentation_five_quotient_unit(self):
        result = audit((2, 2, 3), 5)
        self.assertEqual(result["positive_vectors_checked"], 4368)
        self.assertEqual(result["modular_survivors"], 0)
        self.assertEqual(result["unit_count"], 0)


if __name__ == "__main__":
    unittest.main()
