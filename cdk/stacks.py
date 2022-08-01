import aws_cdk as cdk

from cdk.constructs import Table


class MainStack(cdk.Stack):
    def __init__(self, scope: cdk.Stack, cid: str, **kw):
        self.table = Table(self, "polygon", pk="pk", sk="sk")
