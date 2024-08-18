import json
import boto3
import os

TABLE_NAME = os.getenv("TABLE_NAME")
RESULT_LIMIT = os.getenv("RESULT_LIMIT")

if not TABLE_NAME:
    raise ValueError("TABLE_NAME environment variable is not set")

if not RESULT_LIMIT:
    raise ValueError("RESULT_LIMIT environment variable is not set")

dynamo_client = boto3.client('dynamodb')
dynamo_resource = boto3.resource('dynamodb')
restaurant_table_client = dynamo_resource.Table(TABLE_NAME)


def search_restaurants(theme: str) -> dict:
    response = restaurant_table_client.scan(
        Limit=int(RESULT_LIMIT),
        FilterExpression="contains(themes, :theme)",
        ExpressionAttributeValues={
            ":theme": theme
        }
    )
    return response['Items']


def handler(event, context):
    print(f"event: {event}")
    theme = json.loads(event["body"])["theme"]
    restaurants = search_restaurants(theme)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(restaurants)
    }