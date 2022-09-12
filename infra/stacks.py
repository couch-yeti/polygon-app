import aws_cdk as cdk
from aws_cdk import aws_events

from infra.constructs import Dynamo, Lambda, Queue, Bridge


class ProcessorStack(cdk.NestedStack):
    """Stack controls the automate pull of dividend data"""

    @property
    def queue(self):
        return self.queue.queue

    @property
    def func(self):
        return self.lambda_.function

    def __init__(self, scope: cdk.Stack, cid: str, **kw):
        super.__init__(scope=scope, id=cid, **kw)

        # lambda and queue/dlq
        self.duration = cdk.Duration.seconds(65)
        self.lambda_ = Lambda(
            scope=self, cid="processor", path="src/processor"
        )

        self.queue = Queue(scope=self, cid="processor-queue")
        self.queue.add_target(self.func, max_batch_window=self.duration)


class MainStack(cdk.Stack):
    @property
    def table(self):
        return self.dynamo.table

    @property
    def bus(self):
        return self.bridge.bus

    def __init__(self, scope: cdk.Stack, cid: str, **kw):
        super.__init__(scope=scope, id=cid, **kw)
        self.dynamo = Dynamo(self, "table", pk="pk", sk="sk")
        self.bridge = Bridge(scope=self, cid="bus")

        self.processor = ProcessorStack(self, "service")
    
        self.processor_start_rule = aws_events.EventPattern()

        
