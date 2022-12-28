import os

import boto3 

def send_text_message(session: boto3.Session):

    if not session:
        session = boto3._get_default_session()
    client = session.client("sns")
    client.publish(PhoneNumber=os.getenv("PHONE_NUMBER"))