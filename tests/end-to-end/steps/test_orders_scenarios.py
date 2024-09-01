import json

import requests
from pytest_bdd import when, then, scenarios, parsers
from requests import Response

from e2e_fixtures import  *
from e2e_utils import temporary_queue_subscribed_to_sns, read_sqs_messages, temporary_queue_subscribed_to_event_bus
from place_order_logic import Order

sqs_client = boto3.client("sqs")
sns_client = boto3.client("sns")

scenarios("../features/orders.feature")

@given("A restaurant waiting for orders", target_fixture="restaurant_sqs_queue_url")
def connect_restaurant_to_event_bus(restaurant_notification_topic_arn: str):
    with temporary_queue_subscribed_to_sns(restaurant_notification_topic_arn) as tmp_queue:
        yield tmp_queue.url


@given("A probe on the event bus", target_fixture="event_bus_probe_queue_url")
def connect_probe_to_event_bus(event_bus_name: str):
    with temporary_queue_subscribed_to_event_bus(
            event_bus_name=event_bus_name,
            event_pattern={
                "source": ["big-mouth"]
            }
    ) as tmp_queue:
        yield tmp_queue.url


@when(parsers.parse("The user orders a meal at {restaurant_name}"), target_fixture="place_order_response")
def place_order(order_api_url: str, restaurant_name: str, authenticated_user: AuthenticatedUser) -> Response:
    print(f"placing order at {restaurant_name}")
    return requests.post(
        url=order_api_url,
        headers={
            "Authorization": authenticated_user.id_token,
            "Content-Type": "application/json"
        },
        data=Order(restaurantName=restaurant_name).model_dump_json()
    )

@then("An order ID is returned synchronously")
def check_place_order_response(place_order_response: Response):
    assert place_order_response.status_code == 200, place_order_response.text
    assert "application/json" in place_order_response.headers["Content-Type"]
    body = place_order_response.json()
    assert "orderId" in body
    assert isinstance(body["orderId"], int)

@then(parsers.parse("The restaurant {restaurant_name} is notified of the order"))
def expect_order_id_in_sqs(restaurant_name: str, restaurant_sqs_queue_url: str):

    notifications = read_sqs_messages(
        queue_url=restaurant_sqs_queue_url,
        expected=1,
        timeout_seconds=10
    )

    assert len(notifications) == 1

    order = json.loads(notifications[0]["Message"])
    print(f"restaurant received order {order}")
    assert "orderId" in order
    assert order["restaurantName"] == restaurant_name

@then(parsers.parse("The event bus probe receives an order event for {restaurant_name}"))
def expect_order_event_in_event_bus_probe(restaurant_name: str, event_bus_probe_queue_url: str):

    events = read_sqs_messages(
        queue_url=event_bus_probe_queue_url,
        expected=2,
        timeout_seconds=20
    )
    print(f"events received {events}")

    assert len(events) == 2

    # sort events by detail-type to make the test deterministic since EventBridge does not guarantee order
    events=sorted(events, key=lambda x: x["detail-type"])

    order_placed = events[0]
    assert order_placed["source"] == "big-mouth"
    assert order_placed["detail-type"] == 'order_placed'
    assert order_placed["detail"]["restaurantName"] == restaurant_name

    restaurant_notification = events[1]
    assert restaurant_notification["source"] == "big-mouth"
    assert restaurant_notification["detail-type"] == 'restaurant_notified'
    assert restaurant_notification["detail"]["restaurantName"] == restaurant_name
