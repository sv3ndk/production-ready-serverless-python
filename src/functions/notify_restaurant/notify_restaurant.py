import os
import json
import boto3
from aws_lambda_powertools.logging import Logger

logger = Logger(log_uncaught_exceptions=True)

bus_name = os.getenv("EVENT_BUS_NAME")
if not bus_name:
    raise ValueError("EVENT_BUS_NAME environment variable is not set")

topic_ARN = os.getenv("TOPIC_ARN")
if not bus_name:
    raise ValueError("TOPIC_ARN environment variable is not set")

eventbridge_client = boto3.client("events")
sns_client = boto3.client("sns")


def handler(event, context):

    order = event["detail"]
    sns_client.publish(
        TopicArn=topic_ARN,
        Message=json.dumps(order)
    )

    logger.info(f"notified restaurant of order: {order["orderId"]}")

    eventbridge_client.put_events(
        Entries=[
            {
                "Source": "big-mouth",
                "DetailType": "restaurant_notified",
                "Detail": json.dumps(order),
                "EventBusName": bus_name
            }
        ]
    )
