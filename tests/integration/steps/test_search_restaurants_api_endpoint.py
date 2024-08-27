import os
from collections.abc import Callable

from integration_fixtures import *
import json
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/search_restaurants_api_endpoint.feature")

@given("The search_restaurant handler", target_fixture="search_restaurants_handler")
def search_restaurants(restaurant_table_name: str) -> Callable:
    # re-create the environment variables expected by the Lambda function
    os.environ["TABLE_NAME"] = restaurant_table_name
    os.environ["POWERTOOLS_SERVICE_NAME"] = "production-ready-serverless"
    import search_restaurants
    return search_restaurants.handler

@when(parsers.parse("I search for the restaurant with theme ${theme}"), target_fixture="restaurants_response")
def search_restaurants(search_restaurants_handler: Callable, theme: str) -> dict:
    # re-create the environment variables expected by the Lambda function
    return search_restaurants_handler({
        "body": json.dumps({"theme": theme})
    }, {})

@then(parsers.parse("I get a list of ${count:d} restaurants"))
def check_search_restaurants_count(restaurants_response: dict, count: int):
    assert restaurants_response['statusCode'] == 200
    assert restaurants_response["headers"]['Content-Type'] == "application/json"
    body = json.loads(restaurants_response['body'])
    assert len(body) == count

@then(parsers.parse("All restaurants have the theme ${theme}"))
def check_search_restaurants_count(restaurants_response: dict, theme: str):
    assert restaurants_response['statusCode'] == 200
    assert restaurants_response["headers"]['Content-Type'] == "application/json"
    body = json.loads(restaurants_response['body'])
    for restaurant in body:
        assert theme in restaurant['themes']
