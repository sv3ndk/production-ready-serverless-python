from typing import cast

import boto3
import os

from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel

from aws_xray_sdk.core import patch_all

# patch all boto3 clients to also include x-ray tracing
patch_all()


logger = Logger(log_uncaught_exceptions=True)
web_app = APIGatewayRestResolver(enable_validation=True)


TABLE_NAME = os.getenv("TABLE_NAME")
MATURITY_LEVEL = os.getenv("MATURITY_LEVEL")
SERVICE_NAME = logger.service.replace("-", "_")

if not TABLE_NAME:
    raise ValueError("TABLE_NAME environment variable is not set")

if not MATURITY_LEVEL:
    raise ValueError("PARAM_GROUP environment variable is not set")


dynamo_client = boto3.client('dynamodb')
dynamo_resource = boto3.resource('dynamodb')
restaurant_table_client = dynamo_resource.Table(TABLE_NAME)

def search_restaurants(theme: str, result_limit: int) -> list[dict]:
    response = restaurant_table_client.scan(
        Limit=int(result_limit),
        FilterExpression="contains(themes, :theme)",
        ExpressionAttributeValues={
            ":theme": theme
        }
    )
    return response['Items']

class SearchRestaurantsRequest(BaseModel):
    theme: str

@web_app.post("/restaurants/search")
def search(body: SearchRestaurantsRequest) -> list[dict]:
    result_limit_params = parameters.get_parameter(
            # /production_ready_serverless/shared_context/dev/search_restaurants/config
            name=f"/{SERVICE_NAME}/shared_context/{MATURITY_LEVEL}/search_restaurants/config",
            transform="json",
            max_age=60
        )
    result_limit = int(cast(dict, result_limit_params)["defaultResults"])
    logger.info(f"result_limit_params: {result_limit}")

    some_secret = parameters.get_parameter(
        # /production_ready_serverless/shared_context/dev/search_restaurants/secrets
        name=f"/{SERVICE_NAME}/shared_context/{MATURITY_LEVEL}/search_restaurants/secrets",
        transform=None,
        max_age=60
    )

    restaurants = search_restaurants(theme=body.theme, result_limit=result_limit)
    return restaurants

def handler(event: dict, context: LambdaContext) -> dict:
    return web_app.resolve(event, context)