import os

import boto3
from boto3.dynamodb import table

tbl_name = os.getenv("TABLE")


def get_table(table_name: str = tbl_name, session: boto3.Session=None) -> table:
    """Return a dynamo table object from boto3"""

    if not session:
        session = boto3._get_default_session()
    resource = session.resource("dynamodb")
    return resource.Table(table_name)
