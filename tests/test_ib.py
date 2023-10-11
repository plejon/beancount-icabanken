import pytest
from beancount_icabanken.ib import Ib

@pytest.fixture
def csv_file():
    with open("t.csv", "r") as f:
        return f


def test_import(csv_file):
    ib = Ib({"9274-261 885 6": "Assets:IcaBanken:DebitCard"}, {})
    i = ib.identify(csv_file)
