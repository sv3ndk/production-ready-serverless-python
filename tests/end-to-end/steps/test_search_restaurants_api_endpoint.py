import requests

from end_to_end_fixtures import  *
import json
from pytest_bdd import when, then, scenarios, parsers
from requests import Response

scenarios("../features/search_restaurants_api_endpoint.feature")


@when(parsers.parse("They search for restaurants with theme ${theme}"), target_fixture="restaurants_response")
def get_restaurants(search_restaurant_url: str, theme: str, authenticated_user: AuthenticatedUser) -> Response:
    return requests.post(
        url=search_restaurant_url,
        headers={
            "Authorization": authenticated_user.id_token,
            "Content-Type": "application/json"
        },
        data=json.dumps({"theme": theme})
    )

@then(parsers.parse("A list of {count:d} restaurants is received"))
def check_get_restaurant_count(restaurants_response: Response, count: int):
    assert restaurants_response.status_code == 200
    assert restaurants_response.headers["Content-Type"] == "application/json"
    body = json.loads(restaurants_response.content)
    assert len(body) == count


@then(parsers.parse("All restaurants have the theme ${theme}"))
def check_get_restaurant_count(restaurants_response: Response, theme: str):
    body = json.loads(restaurants_response.content)
    for restaurant in body:
        assert theme in restaurant["themes"]