import requests
from pytest_bdd import when, then, scenarios, parsers
from requests import Response

from e2e_fixtures import  *
from e2e_utils import temporary_queue_subscribed_to_sns, read_message_from_sqs
from place_order_logic import Order

sqs_client = boto3.client("sqs")
sns_client = boto3.client("sns")

scenarios("../features/orders.feature")

@given("A restaurant waiting for orders", target_fixture="restaurant_sqs_queue_url")
def connect_restaurant_to_event_bus(restaurant_notification_topic_arn: str):
    with temporary_queue_subscribed_to_sns(restaurant_notification_topic_arn) as queue_url:
        yield queue_url

@when(parsers.parse("The user orders a meal at {restaurant_name}"), target_fixture="place_order_response")
def place_order(order_api_url: str, restaurant_name: str, authenticated_user: AuthenticatedUser) -> Response:
    return requests.post(
        url=order_api_url,
        headers={
            "Authorization": authenticated_user.id_token,
            "Content-Type": "application/json"
        },
        data=Order(restaurantName=restaurant_name).model_dump_json()
    )

@then("An order ID is returned")
def check_place_order_response(place_order_response: Response):
    assert place_order_response.status_code == 200, place_order_response.text
    assert "application/json" in place_order_response.headers["Content-Type"]
    body = place_order_response.json()
    assert "orderId" in body
    assert isinstance(body["orderId"], int)

@then(parsers.parse("The restaurant {restaurant_name} is notified of the order"))
def expect_order_id_in_sqs(restaurant_name: str, restaurant_sqs_queue_url: str):

    orders = read_message_from_sqs(restaurant_sqs_queue_url)

    assert len(orders) == 1

    order = orders[0]
    assert order.sourceType == "sns"
    assert "orderId" in order.message
    assert order.message["restaurantName"] == restaurant_name
