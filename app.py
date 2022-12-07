import os

import aws_cdk as cdk
from dotenv import load_dotenv

from infra.stacks import MainStack

load_dotenv(".env.shared")
load_dotenv(".env.secret")

app = cdk.App()

name = f"polygon"
stack = MainStack(scope=app, cid=name)

app.synth()
