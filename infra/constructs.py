from typing import Optional

import aws_cdk as cdk
from aws_cdk import (
    aws_dynamodb,
    aws_lambda,
    aws_sqs,
    aws_lambda_event_sources,
    aws_events,
)
from constructs import Construct


class ScheduledEvent(Construct):
    def __init__(self, scope: Construct, cid: str):
        super().__init__(scope=scope, id=cid)


class Bridge(Construct):
    @property
    def bus(self):
        return self._bus

    def __init__(self, scope: Construct, cid: str, **kw):
        super().__init__(scope=scope, id=cid, **kw)

        self._bus = aws_events.EventBus(scope=self, id="bus")

    # def rule(self, )


class Queue(Construct):
    def __init__(
        self,
        scope: Construct,
        cid: str,
        **kw,
    ):
        super().__init__(self, scope=scope, id=cid, **kw)
        self.dlq = self._dlq()
        self.queue = aws_sqs.Queue(
            scope=self,
            id="queue",
            dead_letter_queue=aws_sqs.DeadLetterQueue(
                max_receive_count=5, queue=self.dlq
            ),
        )

    def _dlq(self):
        return aws_sqs.Queue(self, "dlq")

    def add_target(
        self,
        target: aws_lambda.Function,
        max_batch_window: cdk.Duration,
        batch_size: int = 1,
    ):
        # add the target
        target.add_event_source(
            aws_lambda_event_sources.SqsEventSource(
                queue=self.queue,
                batch_size=batch_size,
                max_batching_window=max_batch_window,
            )
        )
        # grant permissions
        self.queue.grant_consume_messages(target)


class Lambda(Construct):
    def __init__(self, scope: Construct, cid: str, path: str, **kw):
        super().__init__(scope=scope, id=cid, **kw)
        self.path = path
        self.function = aws_lambda.Function(
            self,
            id=cid,
            handler="handler.lambda_handler",
            code=self.code(path=self.path),
        )

    def _code(self, path: str) -> aws_lambda.Code:
        return aws_lambda.Code.from_asset(
            path=path,
            bundling=cdk.BundlingOptions(
                image=aws_lambda.Runtime.PYTHON_3_8.bundling_image,
                command=[
                    "bash",
                    "-c",
                    "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output",
                ],
            ),
        )


class Dynamo(Construct):
    def __init__(
        self,
        scope: Construct,
        cid: str,
        pk: str,
        sk: Optional[str] = None,
        **kw,
    ):
        super().__init__(scope=scope, id=cid, **kw)
        self.pk = self.attribute(name=pk)
        self.sk = self.attribute(name=sk)

        self.table = aws_dynamodb.Table(
            scope=self,
            id="table",
            partition_key=self.pk,
            sort_key=self.sk,
            time_to_live_attribute="expiration",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )

    def attribute(self, name: Optional[str] = None) -> aws_dynamodb.Attribute:
        if not name:
            return None
        return aws_dynamodb.Attribute(
            name=name, type=aws_dynamodb.AttributeType.STRING
        )

    def add_gsi(
        self, gsi_name: str, pk: str, sk: Optional[str] = None
    ) -> None:
        """Function adds a GSI to an existing table"""
        gsi_pk = self.attribute(name=pk)
        gsi_sk = self.attribute(name=sk)

        self.table.add_global_secondary_index(
            index_name=gsi_name, partition_key=gsi_pk, sort_key=gsi_sk
        )
