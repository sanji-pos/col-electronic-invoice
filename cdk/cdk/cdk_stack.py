from aws_cdk import (
    Stack,
    Fn,
    aws_iam as iam,
    aws_logs,
    RemovalPolicy
)
from aws_cdk.aws_apigatewayv2 import CfnIntegration, CfnRoute, CfnAuthorizer
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct

class ColElectronicInvoiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        create_invoice_fn = PythonFunction(
            self, "CreateInvoiceLambda",
            entry="./lambda/create_invoice",
            runtime=__import__("aws_cdk.aws_lambda").aws_lambda.Runtime.PYTHON_3_10,
            index="index.py",
            handler="handle",
        )
        
        aws_logs.LogGroup(
            self, "CreateInvoiceLogGroup",
            log_group_name=f"/aws/lambda/{create_invoice_fn.function_name}",
            retention=aws_logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )


        send_test_fn = PythonFunction(
            self, "SendTestLambda",
            entry="./lambda/send_test",
            runtime=__import__("aws_cdk.aws_lambda").aws_lambda.Runtime.PYTHON_3_10,
            index="index.py",
            handler="handle"
        )
        
        aws_logs.LogGroup(
            self, "SendTestLogGroup",
            log_group_name=f"/aws/lambda/{send_test_fn.function_name}",
            retention=aws_logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        api_id = Fn.import_value("sls-sanji-pos-server-prod-HttpApiId")

        authorizer_arn = Fn.import_value(
            "sls-sanji-pos-server-prod-ValidateGatewayTokenAuthorizerLambdaFunctionQualifiedArn"
        )

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
            authorizer_payload_format_version="2.0",
            authorizer_result_ttl_in_seconds=3600,
            enable_simple_responses=True
        )

        def add_route(path: str, method: str, fn: PythonFunction, id_prefix: str):
            integration = CfnIntegration(
                self, f"{id_prefix}Integration",
                api_id=api_id,
                integration_type="AWS_PROXY",
                integration_uri=fn.function_arn,
                integration_method="POST",
                payload_format_version="2.0",
            )

            fn.add_permission(
                f"{id_prefix}InvokePermission",
                principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
                action="lambda:InvokeFunction",
                source_arn=(
                    f"arn:aws:execute-api:{self.region}:{self.account}:"
                    f"{api_id}/*/{method}{path}"
                )
            )

            CfnRoute(
                self, f"{id_prefix}Route",
                api_id=api_id,
                route_key=f"{method} {path}",
                target=f"integrations/{integration.ref}",
                authorization_type="CUSTOM",
                authorizer_id=authorizer.ref,
            )

        add_route("/new-invoice", "POST", create_invoice_fn, "CreateInvoice")
        add_route("/new-send-test", "POST", send_test_fn, "SendTest")
