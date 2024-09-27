import random
import json

import boto3
from pydantic import BaseModel

from aws_xray_sdk.core import patch_all

# patch boto3 client to also include x-ray tracing
patch_all()


class Order(BaseModel):
    restaurantName: str

eventbridge_client = boto3.client("events")

def do_place_order(event: Order, bus_name: str) -> int:
    order_id = random.randint(1000, 9999)

    eventbridge_client.put_events(
        Entries=[
            {
                "Source": "big-mouth",
                "DetailType": "order_placed",
                "Detail": json.dumps({
                    "orderId": order_id,
                    "restaurantName": event.restaurantName
                }),
                "EventBusName": bus_name
            },
        ]
    )

    return order_id
