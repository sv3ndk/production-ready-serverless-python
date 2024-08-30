import json
from typing import cast

import boto3
import os

from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.logging import Logger

logger = Logger(log_uncaught_exceptions=True)

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


def search_restaurants(theme: str, result_limit: int) -> dict:
    response = restaurant_table_client.scan(
        Limit=int(result_limit),
        FilterExpression="contains(themes, :theme)",
        ExpressionAttributeValues={
            ":theme": theme
        }
    )
    return response['Items']


def handler(event, context):
    theme = json.loads(event["body"])["theme"]

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

    restaurants = search_restaurants(theme=theme, result_limit=result_limit)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(restaurants)
    }