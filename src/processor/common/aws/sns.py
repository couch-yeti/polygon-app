import os

import boto3 

def send_text_message(msg:str, session: boto3.Session=None):

    if not session:
        session = boto3._get_default_session()
    client = session.client("sns")
    client.publish(PhoneNumber=os.getenv("PHONE_NUMBER"), Message=msg)