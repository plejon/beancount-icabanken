import os
from csv import DictReader

from beancount.core import data, flags
from beancount.core.number import D
from beancount.core.amount import Amount
from beancount.ingest.importer import ImporterProtocol
from typing import Dict

from beancount_icabanken.loader import IBCSV
from beancount_icabanken.utils import make_date_obj


class Ib(ImporterProtocol):
    def __init__(self, account_info: Dict[str, str], known_transactions: Dict[str, str]):
        self.account_info = account_info
        self.known_transactions = known_transactions

        self.active_account: str = ""
        # self.stat_date: date = None
        # self.end_date: date = None

        super().__init__()

    def load_file(self, file) -> IBCSV:
        with open(file.name, "r", encoding="utf-8-sig") as f:
            lines = [line.strip() for line in f.readlines()]

        account_number = lines.pop(0)

        start_date = lines.pop(0)
        start_date_obj = make_date_obj(start_date)

        end_date = lines.pop(0)
        end_date_obj = make_date_obj(end_date)

        transactions = list(DictReader(lines, delimiter=";"))
        csv_obj = IBCSV(
            account_number=account_number,
            start_date=start_date_obj,
            end_date=end_date_obj,
            transactions=transactions,
            file_name=file.name,
        )

        return csv_obj

    def identify(self, file):
        csv_obj = self.load_file(file)

        if csv_obj.account_number:
            return True

    def extract(self, file, **kwargs):
        csv_obj = self.load_file(file)

        entries = []

        transactions = list(enumerate(csv_obj.transactions, start=1))
        for index, entry in transactions:
            postings = [
                data.Posting(
                    csv_obj.account_number,
                    Amount(D(str(entry.Belopp)), "SEK"),
                    None,
                    None,
                    None,
                    None,
                ),
            ]

            if entry.Text in self.known_transactions:
                typename = self.known_transactions[entry.Text]
            else:
                typename = "Expenses:Unknown"

            postings.append(
                data.Posting(
                    typename,
                    Amount(D(str(entry.Belopp * -1)), "SEK"),
                    None,
                    None,
                    None,
                    None,
                )
            )

            entries.append(
                data.Transaction(
                    meta=data.new_metadata(csv_obj.account_number, index),
                    date=entry.Datum,
                    flag=flags.FLAG_OKAY,
                    payee=entry.Text,
                    narration=entry.Budgetgrupp,
                    tags=set(),
                    links=set(),
                    postings=postings,
                )
            )

        meta = data.new_metadata(csv_obj.file_name, transactions[-1][0])
        data.Balance(
            meta,
            csv_obj.end_date,
            csv_obj.account_number,
            transactions[-1][1].Saldo,
            None,
            None,

        )
        return entries

    def file_account(self, file):
        csv_obj = self.load_file(file)
        return csv_obj.account_number

    def file_date(self, file):
        csv_obj = self.load_file(file)
        return csv_obj.end_date

    def file_name(self, file):
        _, extension = os.path.splitext(os.path.basename(file.name))
        return f"IcaBanken{extension}"
