import json
from typing import cast

import boto3
import os

from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.logging import Logger

logger = Logger(log_uncaught_exceptions=True)
SERVICE_NAME = logger.service.replace("-", "_")

TABLE_NAME = os.getenv("TABLE_NAME")
if not TABLE_NAME:
    raise ValueError("TABLE_NAME environment variable is not set")

MATURITY_LEVEL = os.getenv("MATURITY_LEVEL")
if not MATURITY_LEVEL:
    raise ValueError("PARAM_GROUP environment variable is not set")

dynamo_client = boto3.client('dynamodb')
dynamo_resource = boto3.resource('dynamodb')
restaurant_table_client = dynamo_resource.Table(TABLE_NAME)


def get_restaurants(result_limit: int) -> dict:
    response = restaurant_table_client.scan(Limit=result_limit)
    return response['Items']


def handler(event, context):
    result_limit_params = parameters.get_parameter(
            # /production_ready_serverless/shared_context/dev/get_restaurants/config
            name=f"/{SERVICE_NAME}/shared_context/{MATURITY_LEVEL}/get_restaurants/config",
            transform="json",
            max_age=60
        )
    result_limit = int(cast(dict, result_limit_params)["defaultResults"])
    logger.info(f"result_limit_params: {result_limit}")

    restaurants = get_restaurants(result_limit=result_limit)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(restaurants)
    }