import pytest
from unittest.mock import patch
from func.utils import convertAmountToCent, convertCentToDecimalString

def test_floatInput():
    """
    Test the conversion of float inputs to cents.
    """
    assert convertAmountToCent(140.00) == 14000
    assert convertAmountToCent(140.01) == 14001
    assert convertAmountToCent(140.12) == 14012
    assert convertAmountToCent(99.55) == 9955

    assert convertAmountToCent(100.123, 3) == 100123

def test_stringInput():
    """
    Test the conversion of float inputs to cents.
    """
    assert convertAmountToCent("140.00") == 14000
    assert convertAmountToCent("140.01") == 14001
    assert convertAmountToCent("140.12") == 14012
    assert convertAmountToCent("99.55") == 9955

    assert convertAmountToCent("100.123", 3) == 10012 # ensure two digit
    




