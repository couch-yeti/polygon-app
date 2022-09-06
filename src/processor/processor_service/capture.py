from ast import Div
import json
import os
from typing import List, Dict

from marshmallow import INCLUDE
from polygon import RESTClient

from common.aws import dynamo
from processor_service.data import Dividend

api_key = os.getenv("POLYGON_API_KEY")


def get_records_gte_paid_date(
    ticker: str, paid_date: str
) -> List[Dict[str, str]]:

    client = RESTClient(api_key)

    dividends = client.list_dividends(
        ticker=ticker, pay_date_gte=paid_date, raw=True
    )

    data = dividends.data.decode("utf-8")
    return json.loads(data)["results"]


def convert_dividends(records: List[dict]) -> List[Dividend]:
    """Loads records into Dividends

    Parameters
    ----------
    records : list
        a list of dictionary items from the polygon api

    Returns
    -------
    list
        list of Dividends
    """
    schema = Dividend(unknown=INCLUDE)
    return [schema.load(record) for record in records]


def handle_dividend_records(records: List[dict]) -> None:
    dividends = convert_dividends(records=records)
    schema = Dividend()
    for dividend in dividends:
        dynamo.table.put_item(Item=schema.dump(dividend))
