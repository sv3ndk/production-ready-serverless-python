import botocore.session
import requests

from e2e_fixtures import  *
import json
from pytest_bdd import given, when, then, scenarios, parsers
from requests import Response
from requests_aws4auth import AWS4Auth

scenarios("../features/get_restaurants_api_endpoint.feature")

@given("An IAM authenticated user", target_fixture="auth")
def get_restaurants():
    return AWS4Auth(
        refreshable_credentials=botocore.session.Session().get_credentials(),
        service='execute-api',
        region=boto3.session.Session().region_name
    )

@when("They call the restaurant API endpoint", target_fixture="restaurants_response")
def get_restaurants(get_restaurant_api_url: str, auth) -> Response:
    return requests.get(get_restaurant_api_url, auth=auth)

@then(parsers.parse("They get a list of {count:d} restaurants"))
def check_get_restaurant_count(restaurants_response: Response, count: int):
    assert restaurants_response.status_code == 200
    assert restaurants_response.headers["Content-Type"] == "application/json"
    body = json.loads(restaurants_response.content)
    assert len(body) == count
