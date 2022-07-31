from typing import Optional

from aws_cdk import aws_dynamodb
from constructs import Construct


class Table(Construct):
    def __init__(
        self,
        scope: Construct,
        cid: str,
        pk: str,
        sk: Optional[str] = None,
        **kw
    ):
        self.pk = self.attribute(name=pk)
        self.sk = self.attribute(name=sk)

        self.table = aws_dynamodb.Table(
            scope=self, id="table", partition_key=self.pk, sort_key=self.sk
        )

    def attribute(self, name: Optional[str] = None) -> aws_dynamodb.Attribute:
        if not name:
            return None
        return aws_dynamodb.Attribute(
            name=name, type=aws_dynamodb.AttributeType.STRING
        )
