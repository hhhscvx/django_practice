from django.test import TestCase
from store.logic import operations

class LogicTestCase(TestCase): # python manage.py test store/tests
    def test_plus(self):
        result = operations(6, 12, '+')
        self.assertEqual(18, result)

    def test_minus(self):
        result = operations(7, 12, '-')
        self.assertEqual(-5, result)

    def test_mul(self):
        result = operations(3, 2, '*')
        self.assertEqual(6, result)

