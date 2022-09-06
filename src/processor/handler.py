from datetime import datetime
import json
import os
import re
from typing import List, Dict, Tuple

from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

from common.aws import dynamo, sqs
from processor_service.capture import (
    get_records_gte_paid_date,
    handle_dividend_records,
)

load_dotenv()
logger = Logger(serivce="processor", level=os.getenv("LEVEL", "WARN"))


def get_ticker_list() -> List[str]:
    table = dynamo.get_table()
    expr = Key("pk").eq("ticker")
    query = table.query(
        KeyConditionExpression=expr, ProjectionExpression="ticker"
    )
    return query["Items"]


def group_tickers(
    tickers: List[str], increment: int = 5
) -> Tuple(List[str], List[str]):
    """return of five tickers and returns those in message format"""
    group_to_work = tickers[:increment]
    remaining_tickers = tickers[increment:]
    return group_to_work, remaining_tickers


def work_ticker(ticker: str, today: str) -> None:

    records = get_records_gte_paid_date(
        ticker=ticker,
    )

    handle_dividend_records(records=records)


def parse_payload(event: Dict[str, str]) -> Dict[str, list]:
    """Parses sqs message structure for needed data"""

    return json.loads(event["Records"][0]["body"])


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context=None):
    """Get all tickers and drop messages for each batch into queue"""

    record = parse_payload(event)

    if record.get("start"):

        tickers = get_ticker_list()
        return sqs.send(message=json.dumps({"tickers": tickers}))

    today = datetime.today()
    tickers_to_work, remaining_tickers = group_tickers(tickers)
    logger.info(f"Working the following tickers: {tickers_to_work}")

    # work tickets here meaning
    # 1. get the dividend info from polygon
    # 2. convert to dividend schema
    # 3. place in dynamo
    # 4. if end of tickets to work send text message to phone

    for ticker in tickers_to_work:
        work_ticker(ticker=ticker, today=today.strftime("%d-%m-%Y"))
    
    message = json.dumps({"tickers": remaining_tickers})
    sqs.send(message)
