import os
import json
import boto3
import random

bus_name = os.getenv("EVENT_BUS_NAME")
if not bus_name:
    raise ValueError("EVENT_BUS_NAME environment variable is not set")

eventbridge_client = boto3.client("events")


def handler(event, context):
    restaurant_name = json.loads(event["body"])["restaurantName"]
    order_id = random.randint(1000, 9999)

    eventbridge_client.put_events(
        Entries=[
            {
                "Source": "big-mouth",
                "DetailType": "order_placed",
                "Detail": json.dumps({
                    "orderId": order_id,
                    "restaurantName": restaurant_name
                }),
                "EventBusName": bus_name
            }
        ]
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"orderId": order_id})
    }
