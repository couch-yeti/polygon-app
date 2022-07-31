from __future__ import annotations
from datetime import datetime
import json
import os
from tabnanny import check
from typing import List, Dict

import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from marshmallow import Schema, fields, INCLUDE, post_dump
from polygon import RESTClient

from src.api.service.aws import dynamo


"""Dynamo schema

I'm going to need to get all tickers for a given month and that data point should include
    * the total already received for the given month 
    * the total known that we are yet to receive

I need to be able to get the next payments for a certain amount of days in the future 

I'm storing the 
    """


load_dotenv(".env.shared")
load_dotenv(".env.secret")
api_key = os.getenv("POLYGON_API_KEY")


class Dividend:
    def __init__(self, cash_amount, **kw):
        self.cash_amount = cash_amount
        self.kw = kw

    def asdict(self):
        now = datetime.now()
        return {
            "pk": self.kw["ticker"],
            "sk": datetime.timestamp(now),
            "timestamp": datetime.timestamp(now),
            **self.kw,
        }


class DividendSchema(Schema):
    ticker = fields.String()
    declaration_date = fields.Date()
    ex_dividend_date = fields.Date()
    frequency = fields.Int()
    pay_date = fields.Date()
    cash_amount = fields.Decimal(places=3)
    record_date = fields.Date()

    @post_dump
    def dynamo_record(self, data, **kwargs):
        return {
            "pk": data["ticker"],
            "sk": data["pay_date"],
            "text_sent": None,
            **data,
        }


dt = "2022-06-17"


def get_dividends_gte_paid_date(
    ticker: str, paid_date: str
) -> List[Dict[str, str]]:

    client = RESTClient(api_key)

    dividends = client.list_dividends(
        ticker=ticker, pay_date_gte=paid_date, raw=True
    )

    data = dividends.data.decode("utf-8")
    return json.loads(data)["results"]


def deserialize(data: List[Dict[str, str]]) -> List[Dividend]:
    schema = DividendSchema(unknown=INCLUDE)
    return [schema.load(i) for i in data]


def check_and_insert_record(
    dividend: Dividend, table_name=os.getenv("TABLE")
) -> None:
    """Function checks if the record exists in the DB if not it inserts it"""
    table = dynamo.table(table_name=table_name)
    expression = Key("pk").eq(dividend["pk"]) & Key("sk").eq(dividend["sk"])
    query = table.query(KeyConditionExpression=expression)["Items"]
    if not query:
        table.put_item(Item=dividend)


dividends = [
    {
        "cash_amount": 0.1809,
        "currency": "USD",
        "declaration_date": "2022-07-15",
        "dividend_type": "CD",
        "ex_dividend_date": "2022-07-18",
        "frequency": 12,
        "pay_date": "2022-07-26",
        "record_date": "2022-07-19",
        "ticker": "QYLD",
    },
    {
        "cash_amount": 0.1735,
        "currency": "USD",
        "declaration_date": "2022-06-17",
        "dividend_type": "CD",
        "ex_dividend_date": "2022-06-21",
        "frequency": 12,
        "pay_date": "2022-06-29",
        "record_date": "2022-06-22",
        "ticker": "QYLD",
    },
]

"""I need to store any dividend that has been declared but not paid yet 

Ultimate goal is to text my phone and let me know if i'm getting 
a new dividend soon and when for my whole portfolio. 

Later build a process that shows how much I've made from all of my 
dividend stocks and how much I've made for each one.

So for every declared dividend:
    grab the paid date and see if it's the same 
        potentially we can use the paid date as the sort key
        of the table and query the ticker symbol and the sort key
        to see if it exists.  If it doesn't exist then place the
        record in the dynamo and include a flag for whether a text
        has been sent."""

boto3.setup_default_session(profile_name="dev")
data = deserialize(dividends)
schema = DividendSchema()
for item in data:
    dividend = schema.dump(item)
    check_and_insert_record(dividend)
