import os

from prsl_fixtures import *
import json
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/search_restaurants_api_endpoint.feature")

@given(parsers.parse("I search for the restaurant with theme ${theme}"), target_fixture="restaurants_response")
def get_index_page(restaurant_table_name: str, theme: str) -> dict:
    # re-create the environment variables expected by the Lambda function
    os.environ["TABLE_NAME"] = restaurant_table_name
    os.environ["RESULT_LIMIT"] = "20"
    import search_restaurants
    return search_restaurants.handler({
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
