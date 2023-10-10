from decimal import Decimal
from textwrap import dedent
from datetime import datetime, date
from csv import DictReader
import pytest

from beancount_icabanken.loader import IBCSV, IBTransaction


@pytest.fixture
def tmp_file_pass(tmp_path):
    x = tmp_path / "transactions.csv"
    x.write_text(
        dedent(
            """
            9274-123 456 7
            Datum;Text;Typ;Budgetgrupp;Belopp;Saldo
            2023-10-01;Crv Maxi Ica Stormarkn ; Korttransaktion;Övrigt;-192,75 kr;-19 961,17 kr
            2023-10-01    ;Crv Maxi Ica Stormarkn;Korttransaktion;Övrigt;-10,00 kr;-19 768,42 kr
            2023-09-28;Crv Ok-Varuhall;  Korttransaktion;Övrigt;-96,00 kr;-19 758,42 kr
            """
        ).strip()
    )
    return x


def test_ibcsv_pass(tmp_file_pass):
    with open(tmp_file_pass) as f:
        lines = [l.strip() for l in f.readlines()]

    account_number = lines.pop(0)
    transactions = list(DictReader(lines, delimiter=";"))

    case = IBCSV(account_number=account_number, transactions=transactions, file_name=tmp_file_pass.name)

    assert case.account_number == "9274-123 456 7"

    assert case.transactions[0].Datum == date(2023, 10, 1)
    assert case.transactions[0].Text == "Crv Maxi Ica Stormarkn"
    assert case.transactions[0].Typ == "Korttransaktion"
    assert case.transactions[0].Budgetgrupp == "Övrigt"
    assert case.transactions[0].Belopp == -192.75
    assert case.transactions[0].Saldo == -19961.17

    assert case.transactions[1].Datum == date(2023, 10, 1)
    assert case.transactions[1].Text == "Crv Maxi Ica Stormarkn"
    assert case.transactions[1].Typ == "Korttransaktion"
    assert case.transactions[1].Budgetgrupp == "Övrigt"
    assert case.transactions[1].Belopp == -10.00
    assert case.transactions[1].Saldo == -19768.42

    assert case.transactions[2].Datum == date(2023, 9, 28)
    assert case.transactions[2].Text == "Crv Ok-Varuhall"
    assert case.transactions[2].Typ == "Korttransaktion"
    assert case.transactions[2].Budgetgrupp == "Övrigt"
    assert case.transactions[2].Belopp == -96.00
    assert case.transactions[2].Saldo == -19758.42


##### Validate Account Number #####
@pytest.mark.parametrize(
    "account,expected",
    [
        ("  9274-123 456 7", "9274-123 456 7"),
        ("9274-123 456 6     ", "9274-123 456 6"),
        ("   9274-123 456 5     ", "9274-123 456 5"),
        ("9274-123 456 4", "9274-123 456 4"),
    ],
)
def test_ibcsv_account_number_pass(account, expected):
    case = IBCSV.validate_account_number(account)
    assert case == expected


@pytest.mark.parametrize(
    "datum,expected",
    [
        ("9274-123 4 56 7", ""),
        ("9274123 456 7", ""),
        ("9274-123456 7", ""),
    ],
)
def test_ibcsv_account_number_fail(datum, expected):
    with pytest.raises(ValueError):
        case = IBTransaction.validate_datum(datum)
        assert case == expected


##### Validate Datum #####
@pytest.mark.parametrize(
    "datum,expected",
    [
        ("  2023-10-01", date(2023, 10, 1)),
        ("2023-10-02   ", date(2023, 10, 2)),
        ("   2023-10-03   ", date(2023, 10, 3)),
        ("2023-10-04", date(2023, 10, 4)),
    ],
)
def test_ibcsv_datum_pass(datum, expected):
    case = IBTransaction.validate_datum(datum)
    assert case == expected


@pytest.mark.parametrize(
    "datum,expected",
    [
        ("20231001", ""),
        ("23-10-02", ""),
        ("03-10-2023", ""),
    ],
)
def test_ibcsv_datum_fail(datum, expected):
    with pytest.raises(ValueError):
        IBTransaction.validate_datum(datum)


#### Validate Belopp / Saldo #####
@pytest.mark.parametrize(
    "belopp,expected",
    [
        ("-192,75 kr", -192.75),
        ("-1 192,75 kr", -1192.75),
        ("   200 510,00 kr     ", 200510.0),
        ("-150 512,94 kr", -150512.94),
    ],
)
def test_ibcsv_account_amount_pass(belopp, expected):
    case1 = IBTransaction.validate_belopp(belopp)
    assert float(case1) == expected

    case2 = IBTransaction.validate_saldo(belopp)
    assert float(case2) == expected


@pytest.mark.parametrize(
    "belopp,expected",
    [
        ("-192,75kr", ""),
        ("11927.5kr", ""),
    ],
)
def test_ibcsv_account_amount_fail(belopp, expected):
    with pytest.raises(ValueError):
        IBTransaction.validate_belopp(belopp)

    with pytest.raises(ValueError):
        IBTransaction.validate_saldo(belopp)
