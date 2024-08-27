import os
from typing import Callable

from integration_fixtures import *
from bs4 import BeautifulSoup
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/index_page.feature")

@given("The get_index lambda", target_fixture="get_index_handler")
def get_get_index_handler(app_restaurant_url: str, cognito_user_pool_id: str, cognito_web_user_pool_client_id: str) -> Callable:
    # re-create the environment variables expected by the Lambda function
    os.environ["RESTAURANTS_API_URL"] = app_restaurant_url
    os.environ["COGNITO_USER_POOL_ID"] = cognito_user_pool_id
    os.environ["COGNITO_CLIENT_ID"] = cognito_web_user_pool_client_id
    os.environ["POWERTOOLS_SERVICE_NAME"] = "production-ready-serverless"
    import get_index
    return get_index.handler

@when("I navigate to the main page", target_fixture="index_response")
def get_index_page(get_index_handler) -> dict:
    return get_index_handler({}, {})

@then("I see the big mouth logo")
def check_big_mouth_logo(index_response: dict):
    assert index_response['statusCode'] == 200
    assert index_response["headers"]['Content-Type'] == "text/html"
    soup = BeautifulSoup(index_response['body'], "html.parser")
    assert soup.find("img", id="logo", src="https://d2qt42rcwzspd6.cloudfront.net/manning/big-mouth.png") is not None

@then(parsers.parse("I see {count:d} restaurants"))
@then("I see {count:d} restaurants")
def check_restaurants_count(index_response: dict, count: int):
    assert index_response['statusCode'] == 200
    assert index_response["headers"]['Content-Type'] == "text/html"
    soup = BeautifulSoup(index_response['body'], "html.parser")
    restaurants = soup.find_all("li", class_="restaurant")
    assert len(restaurants) == count