from requests import Response

from end_to_end_fixtures import *
from bs4 import BeautifulSoup
import requests
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/index_page.feature")

@given("A unauthenticated user", target_fixture="auth")
def get_no_auth():
    return None

@when("They visit the main page", target_fixture="index_response")
def get_index_page(app_root_url: str, auth) -> Response:
    return requests.get(app_root_url, auth=auth)

@then("They see the big mouth logo")
def check_big_mouth_logo(index_response: Response):
    assert index_response.status_code == 200
    assert index_response.headers["Content-Type"] == "text/html"
    soup = BeautifulSoup(index_response.content, "html.parser")
    assert soup.find("img", id="logo", src="https://d2qt42rcwzspd6.cloudfront.net/manning/big-mouth.png") is not None

@then(parsers.parse("They see {count:d} restaurants"))
def check_restaurants_count(index_response: Response, count: int):
    assert index_response.status_code == 200
    assert index_response.headers["Content-Type"] == "text/html"
    soup = BeautifulSoup(index_response.content, "html.parser")
    restaurants = soup.find_all("li", class_="restaurant")
    assert len(restaurants) == count