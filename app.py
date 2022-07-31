import aws_cdk as cdk

app = cdk.App()

name = f"polygon-"
stack = MainStack(scope=app, id=name)
