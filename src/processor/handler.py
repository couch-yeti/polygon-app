from datetime import datetime
import json
import os
from typing import List, Dict, Tuple

from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

from common.aws import dynamo, sqs
from processor_service.capture import (
    get_records_gte_paid_date,
    handle_dividend_records,
)

load_dotenv(".env.shared")
load_dotenv(".env.secret")
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
) -> Tuple[List[str], List[str]]:
    """return first five tickers and returns those in message format"""
    group_to_work = tickers[:increment]
    remaining_tickers = tickers[increment:]
    return group_to_work, remaining_tickers


def work_tickers(tickers: str, today: str) -> None:
    """Get dividend data from API and insert into dyanmo"""
    today = datetime.today()
    for ticker in tickers:
        records = get_records_gte_paid_date(
            ticker=ticker, paid_date=today.strftime("%d-%m-%Y")
        )

        handle_dividend_records(records=records)


def parse_payload(event: Dict[str, str]) -> Dict[str, list]:
    """Parses sqs message structure for needed data"""

    payload = json.loads(event["Records"][0]["body"])
    logger.info(f"parsed payload {payload}")
    return payload


@logger.inject_lambda_context(log_event=True, clear_state=True)
def lambda_handler(event, context=None):
    """Get all tickers and drop messages for each batch into queue"""

    record = parse_payload(event)

    if record.get("start"):

        tickers = get_ticker_list()
        return sqs.send(message=json.dumps({"tickers": tickers}))

    tickers_to_work, remaining_tickers = group_tickers(tickers)
    logger.info(f"Working the following tickers: {tickers_to_work}")

    # work tickets here meaning
    # 1. get the dividend info from polygon
    # 2. convert to dividend schema
    # 3. place in dynamo
    # 4. if end of tickets to work send text message to phone
    work_tickers(tickers=tickers_to_work)

    if remaining_tickers:
        message = json.dumps({"tickers": remaining_tickers})
        sqs.send(message)
    else:

