import json
from typing import cast

import boto3
import os

from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.logging import Logger

logger = Logger(log_uncaught_exceptions=True)

TABLE_NAME = os.getenv("TABLE_NAME")
STAGE_NAME = os.getenv("STAGE_NAME")
SERVICE_NAME = logger.service

if not TABLE_NAME:
    raise ValueError("TABLE_NAME environment variable is not set")

if not STAGE_NAME:
    raise ValueError("STAGE_NAME environment variable is not set")

dynamo_client = boto3.client('dynamodb')
dynamo_resource = boto3.resource('dynamodb')
restaurant_table_client = dynamo_resource.Table(TABLE_NAME)


def get_restaurants(result_limit: int) -> dict:
    response = restaurant_table_client.scan(Limit=result_limit)
    return response['Items']


def handler(event, context):
    result_limit_params = parameters.get_parameter(
            name=f"/{SERVICE_NAME}/stage-{STAGE_NAME}/get-restaurants/config",
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