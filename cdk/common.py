from pathlib import Path
import os

import aws_cdk as cdk
from aws_cdk import aws_lambda


def get_project_root():
    path = Path(os.path.dirname(__file__)).resolve()
    while True:
        if "pyproject.toml" in os.listdir(path):
            return path
        if path == Path("/"):
            break
        path = path.parent
    return None


def get_lambda_asset(path: str)->aws_lambda.Code:
    """Get the lambda asset"""

    _path = str((get_project_root() / path).resolve())
    return (
        aws_lambda.Code.from_asset(
            path=str(_path),
            bundling=cdk.BundlingOptions(
                image=aws_lambda.Runtime.PYTHON_3_8.bundling_image,
                command=[
                    "bash",
                    "-c",
                    "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output",
                ],
            ),
        )
        if os.getenv("local", False)
        else aws_lambda.Code.from_asset(path=str(_path))
    )
