import sys
sys.path.append(".")

from beancount_icabanken.ib import Ib

known_transactions = {
    "Unionen": "Expenses:Union",
    "Klarna Bank Ab": "Expenses:Shopping",
    "Parkster / Billogram": "Expenses:Car:Parking",
    "Convini": "Expenses:Fika",
    "Trygg-Hansa": "Expenses:Insurance",
    "Vw-Finans": "Expenses:Car:Insurance",

}
ib_account_info = {
    "9274-261 885 6": "Assets:IcaBanken:DebitCard",
    "9274-123 824 9": "Assets:IcaBanken:CreditCard",
}

CONFIG = [Ib(ib_account_info, known_transactions)]
