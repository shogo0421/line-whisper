import os
from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apiGW,
)
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambdaLayer = _lambda.LayerVersion(
            self,
            "lambdaLayer",
            code=_lambda.Code.from_asset(join(dirname(__file__), "../lambda")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        webhookLambda = _lambda.Function(
            self,
            "ApiLambda",
            handler="lineWebhook.lambda_handler",
            function_name="lineWebhookFunction",
            code=_lambda.Code.from_asset(join(dirname(__file__), "../lambda/src")),
            timeout=Duration.seconds(60 * 5),
            layers=[lambdaLayer],
            runtime=_lambda.Runtime.PYTHON_3_9,
        )

        webhookLambda.add_environment(
            "LINE_CHANNEL_ACCESS_TOKEN", LINE_CHANNEL_ACCESS_TOKEN
        )
        webhookLambda.add_environment("LINE_CHANNEL_SECRET", LINE_CHANNEL_SECRET)
        webhookLambda.add_environment("OPENAI_API_KEY", OPENAI_API_KEY)

        api = apiGW.RestApi(
            self,
            "line-webhook-api",
            rest_api_name="line whisper",
            default_cors_preflight_options=apiGW.CorsOptions(
                allow_origins=apiGW.Cors.ALL_ORIGINS,
                allow_methods=apiGW.Cors.ALL_METHODS,
                allow_headers=apiGW.Cors.DEFAULT_HEADERS,
                status_code=200,
            ),
        )

        webhookLambdaIntegration = apiGW.LambdaIntegration(webhookLambda)
        apiOrigin = api.root.add_resource("api")
        apiOrigin.add_method("POST", webhookLambdaIntegration)
        apiOrigin.add_method("GET", webhookLambdaIntegration)
