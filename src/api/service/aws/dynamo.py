import os

import boto3
from boto3.dynamodb import table


def table(
    table_name: str = os.getenv("TABLE"), session: boto3.Session = None
) -> table:
    """Function returns a dynamodb table for queries and inserts"""

    if not session:
        session = boto3._get_default_session()

    r = session.resource("dynamodb")
    return r.Table(table_name)
