"""
Sample tests
"""
from django.test import SimpleTestCase
from . import calc


class CalcTests(SimpleTestCase):
    """Test the calc module."""

    def test_add_numbers(self):
        """Test adding numbers together."""
        res = calc.add(5, 6)

        self.assertEquals(res, 11)

    def test_subtract_numbers(self):
        """Test subtracting numbers."""

        res = calc.subtract(10, 15)

        self.assertEquals(res, 5)
