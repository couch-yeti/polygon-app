import os

import aws_cdk as cdk
from aws_cdk import aws_events, aws_events_targets as targets

from infra.constructs import Dynamo, Lambda, Queue, Bridge


class MainStack(cdk.Stack):
    @property
    def table(self):
        return self.dynamo.table

    @property
    def bus(self):
        return self.bridge.bus

    @property
    def func(self):
        return self.lambda_.function

    @property
    def queue(self):
        return self.queue_.queue

    def __init__(self, scope: cdk.Stack, cid: str, **kw):
        super().__init__(scope=scope, id=cid, **kw)
        self.dynamo = Dynamo(self, "table", pk="pk", sk="sk")
        self.add_queue_and_lambda()
        self.create_bus()
        self.prep_assets()

    def add_queue_and_lambda(self):
        # lambda and queue/dlq
        self.duration = cdk.Duration.seconds(65)
        self.lambda_ = Lambda(
            scope=self, cid="processor", path="src/processor"
        )

        self.queue_ = Queue(scope=self, cid="processor-queue")
        self.queue_.add_target(self.func, max_batch_window=self.duration)
        self.queue.grant_send_messages(self.func)
        self.queue.grant_consume_messages(self.func)

    def create_bus(self):

        self.bridge = Bridge(scope=self, cid="bus")
        self.rule = aws_events.Rule(
            self,
            "rule",
            schedule=aws_events.Schedule.rate(cdk.Duration.hours(24)),
        )

    def prep_assets(self):
        """Add env vars to lambdas and grant access"""

        self.func.add_environment(
            key="POLYGON_API_KEY", value="Cats"  # os.getenv("POLYGON_API_KEY")
        )
        self.table.grant_read_write_data(self.func)
        self.bus.grant_put_events_to(self.func)
        self.rule.add_target(
            targets.SqsQueue(
                self.queue,
                message=aws_events.RuleTargetInput.from_object(
                    {"start": True}
                ),
            )
        )
