from aws_cdk import (
    Stack,
    Fn,
    aws_iam as iam,
    aws_apigatewayv2 as apigwv2,
)
from aws_cdk.aws_apigatewayv2 import CfnIntegration, CfnRoute, CfnAuthorizer
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct

class ColElectronicInvoiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Your Lambdas
        create_invoice_fn = PythonFunction(
            self, "CreateInvoiceLambda",
            entry="./lambda/create_invoice",
            runtime=__import__("aws_cdk.aws_lambda").aws_lambda.Runtime.PYTHON_3_10,
            index="index.py",
            handler="handle"
        )

        send_test_fn = PythonFunction(
            self, "SendTestLambda",
            entry="./lambda/send_test",
            runtime=__import__("aws_cdk.aws_lambda").aws_lambda.Runtime.PYTHON_3_10,
            index="index.py",
            handler="handle"
        )

        # 2. Import the existing API URL & extract its API ID
        api_id = Fn.import_value("sls-sanji-pos-server-prod-HttpApiId")

        # 3. Import the Lambda-authorizer ARN
        authorizer_arn = Fn.import_value(
            "sls-sanji-pos-server-prod-ValidateGatewayTokenAuthorizerLambdaFunctionQualifiedArn"
        )

        # 4. Define a CfnAuthorizer
        authorizer = CfnAuthorizer(
            self, "TokenAuthorizer",
            api_id=api_id,
            authorizer_type="REQUEST",
            name="TokenAuthorizer",
            identity_source=["$request.header.Authorization"],
            authorizer_uri=(
                f"arn:aws:apigateway:{self.region}:lambda:"
                f"path/2015-03-31/functions/{authorizer_arn}/invocations"
            ),
            authorizer_payload_format_version="2.0"
        )

        # 5. Helper to add a route + integration + permissions
        def add_route(path: str, method: str, fn: PythonFunction, id_prefix: str):
            # 5a. Integration
            integration = CfnIntegration(
                self, f"{id_prefix}Integration",
                api_id=api_id,
                integration_type="AWS_PROXY",
                integration_uri=fn.function_arn,
                integration_method="POST",
                payload_format_version="2.0",
            )

            # 5b. Grant API Gateway permission to invoke the Lambda
            fn.add_permission(
                f"{id_prefix}InvokePermission",
                principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                action="lambda:InvokeFunction",
                source_arn=(
                    f"arn:aws:execute-api:{self.region}:{self.account}:"
                    f"{api_id}/*/{method}{path}"
                )
            )

            # 5c. Route
            CfnRoute(
                self, f"{id_prefix}Route",
                api_id=api_id,
                route_key=f"{method} {path}",
                target=f"integrations/{integration.ref}",
                authorization_type="CUSTOM",
                authorizer_id=authorizer.ref
            )

        # 6. Wire up your two endpoints
        add_route("/new-invoice", "POST", create_invoice_fn, "CreateInvoice")
        add_route("/new-send-test", "POST", send_test_fn, "SendTest")
