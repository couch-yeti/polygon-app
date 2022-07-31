import aws_cdk as cdk

from cdk import constructs

class MainStack(cdk.Stack):
    def __init__(self, scope: cdk.Stack, cid: str, **kw):
        self.table =
