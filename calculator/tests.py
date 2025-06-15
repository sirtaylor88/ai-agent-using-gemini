"""Unit tests."""

# from contextlib import nullcontext as does_not_raise

# import pytest
# from pkg.calculator import Calculator


# @pytest.fixture(name="calculator")
# def build_calculator() -> Calculator:
#     """Make a calculator."""
#     return Calculator()


# @pytest.mark.parametrize(
#     "expression, expected, expectation",
#     [
#         ("3 + 5", 8, does_not_raise),
#         ("10 - 4", 6, does_not_raise),
#         ("3 * 4", 12, does_not_raise),
#         ("10 / 2", 5, does_not_raise),
#         ("3 * 4 + 5", 17, does_not_raise),
#         ("2 * 3 - 8 / 2 + 5", 7, does_not_raise),
#         ("", None, does_not_raise),
#         ("$ 3 5", None, pytest.raises(ValueError)),
#         ("+ 3", None, pytest.raises(ValueError)),
#     ],
# )
# def test_math_operations(calculator, expression, expected, expectation):
#     with expectation:
#         assert calculator.evaluate(expression) == expected

import unittest

from pkg.calculator import Calculator


class TestCalculator(unittest.TestCase):
    """Calculator test cases."""

    def setUp(self):
        self.calculator = Calculator()

    def test_addition(self):
        """Test addition."""
        result = self.calculator.evaluate("3 + 5")
        self.assertEqual(result, 8)

    def test_subtraction(self):
        """Test substraction."""
        result = self.calculator.evaluate("10 - 4")
        self.assertEqual(result, 6)

    def test_multiplication(self):
        """Test multiplication."""
        result = self.calculator.evaluate("3 * 4")
        self.assertEqual(result, 12)

    def test_division(self):
        """Test division."""
        result = self.calculator.evaluate("10 / 2")
        self.assertEqual(result, 5)

    def test_nested_expression(self):
        """Test nested expression."""
        result = self.calculator.evaluate("3 * 4 + 5")
        self.assertEqual(result, 17)

    def test_complex_expression(self):
        """Test complex expression."""
        result = self.calculator.evaluate("2 * 3 - 8 / 2 + 5")
        self.assertEqual(result, 7)

    def test_empty_expression(self):
        """Test empty expression."""
        result = self.calculator.evaluate("")
        self.assertIsNone(result)

    def test_invalid_operator(self):
        """Test invalid operator."""
        with self.assertRaises(ValueError):
            self.calculator.evaluate("$ 3 5")

    def test_not_enough_operands(self):
        """Test not enough operands."""
        with self.assertRaises(ValueError):
            self.calculator.evaluate("+ 3")


if __name__ == "__main__":
    unittest.main()
