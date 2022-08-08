from itertools import islice
import json
import os
from typing import List, Dict

from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

from manager.aws import dynamo, sqs

load_dotenv()
logger = Logger(serivce="manager", level=os.getenv("LEVEL", "WARN"))


def get_tickers():
    table = dynamo.get_table()
    expr = Key("pk").eq("ticker")
    query = table.query(
        KeyConditionExpression=expr, ProjectionExpression="ticker"
    )
    return query["Items"]


def group_tickers(tickers: List[str], increment: int = 5) -> List[str]:
    """Yield batches of five tickers and returns those in message format"""
    while tickers:
        group = list(islice(tickers, increment))
        yield group
        iterable = iterable[len(group) :]


def parse_payload(event: Dict[str, str]) -> Dict[str, list]:
    record = json.loads(event["Records"][0]["body"])


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context=None):
    """Get all tickers and drop messages for each batch into queue"""

    if event.get("start"):

        tickers = get_tickers()
        return sqs.send(message=json.dumps({"tickers": tickers}))

    groups = group_tickers(tickers)
    for group in groups:
        logger.info(f"SENDING GROUP: {group}")
        message = json.dumps({"tickers": group})
        sqs.send(message)
