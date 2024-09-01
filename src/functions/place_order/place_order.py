import os

from aws_lambda_powertools.event_handler import APIGatewayRestResolver

from place_order_logic import Order, do_place_order

web_app = APIGatewayRestResolver(enable_validation=True)

bus_name = os.getenv("EVENT_BUS_NAME")
if not bus_name:
    raise ValueError("EVENT_BUS_NAME environment variable is not set")


@web_app.post("/orders")
def place_order(event: Order) -> dict:
    order_id = do_place_order(event, bus_name)
    return {"orderId": order_id}


def handler(event, context):
    return web_app.resolve(event, context)