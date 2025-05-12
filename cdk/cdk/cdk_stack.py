from aws_cdk import (
    Stack,
    aws_lambda
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction

from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        createInvoiceLambda = PythonFunction(
            self,
            "createInvoiceLambda",
            entry="./lambda/create_invoice",
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            index="index.py",
            handler="handle"
        )
        sendTestLambda = PythonFunction(
            self,
            "sendTestLambda",
            entry="./lambda/send_test",
            runtime=aws_lambda.Runtime.PYTHON_3_10,
            index="index.py",
            handler="handle"
        )


