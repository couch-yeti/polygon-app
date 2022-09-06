import os

import boto3


def send(
    message: str,
    url: str = os.getenv("SQS_URL"),
    session: boto3.Session = None,
) -> None:
    if not session:
        session = boto3._get_default_session()
    client = session.client("sqs")
    client.send_message(QueueUrl=url, MessageBody=message)
