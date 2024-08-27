import os
from typing import Callable

from integration_fixtures import *
import json
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/get_restaurants_api_endpoint.feature")

@given("The get_restaurant handler", target_fixture="get_restaurants_handler")
def get_restaurants(restaurant_table_name: str) -> Callable:
    # re-create the environment variables expected by the Lambda function
    os.environ["TABLE_NAME"] = restaurant_table_name
    os.environ["POWERTOOLS_SERVICE_NAME"] = "production-ready-serverless"
    import get_restaurants
    return get_restaurants.handler

@when("I call the restaurant API endpoint", target_fixture="restaurants_response")
def get_restaurants(get_restaurants_handler) -> dict:
    return get_restaurants_handler({}, {})

@then(parsers.parse("I get a list of {count:d} restaurants"))
def check_get_restaurant_count(restaurants_response: dict, count: int):
    assert restaurants_response['statusCode'] == 200
    assert restaurants_response["headers"]['Content-Type'] == "application/json"
    body = json.loads(restaurants_response['body'])
    assert len(body) == count
