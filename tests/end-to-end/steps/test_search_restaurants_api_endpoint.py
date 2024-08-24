from dataclasses import dataclass

import faker
import requests

from end_to_end_fixtures import  *
import json
from pytest_bdd import given, when, then, scenarios, parsers
from requests import Response

scenarios("../features/search_restaurants_api_endpoint.feature")


@dataclass
class AuthenticatedUser:
    username: str
    first_name: str
    last_name: str
    id_token: str


@given("A Cognito authenticated user", target_fixture="authenticated_user")
def get_authenticated_user(cognito_user_pool_id: str, cognito_server_user_pool_client_id: str) -> AuthenticatedUser:
    first_name = faker.Faker().first_name()
    last_name = faker.Faker().last_name()
    password = faker.Faker().password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    email = faker.Faker().email()

    cognito_client = boto3.client('cognito-idp')
    create_response = cognito_client.admin_create_user(
        UserPoolId=cognito_user_pool_id,
        Username=email,
        MessageAction='SUPPRESS',
        TemporaryPassword=password,
        UserAttributes=[
            {"Name": "given_name", "Value": first_name},
            {"Name": "family_name", "Value": last_name},
            {"Name": "email", "Value": email}
        ]
    )

    auth_response = cognito_client.admin_initiate_auth(
        AuthFlow='ADMIN_NO_SRP_AUTH',
        UserPoolId=cognito_user_pool_id,
        ClientId=cognito_server_user_pool_client_id,
        AuthParameters={
            "USERNAME": email,
            "PASSWORD": password
        }
    )

    challenge_response = cognito_client.admin_respond_to_auth_challenge(
        UserPoolId=cognito_user_pool_id,
        ClientId=cognito_server_user_pool_client_id,
        ChallengeName=auth_response['ChallengeName'],
        Session=auth_response['Session'],
        ChallengeResponses={
            "USERNAME": email,
            "NEW_PASSWORD": password
        }
    )

    yield AuthenticatedUser(
        username=email,
        first_name=first_name,
        last_name=last_name,
        id_token=challenge_response['AuthenticationResult']['IdToken']
    )

    cognito_client.admin_delete_user(
        UserPoolId=cognito_user_pool_id,
        Username=email
    )


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

@then(parsers.parse("They get a list of ${count:d} restaurants"))
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