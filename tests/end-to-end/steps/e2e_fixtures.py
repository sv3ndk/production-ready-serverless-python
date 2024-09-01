import os
from dataclasses import dataclass

import faker
from pytest import fixture
import boto3
from pytest_bdd import given

cfn_client = boto3.client('cloudformation')

# -------------------
# pytest fixtures

@fixture
def feature_name() -> str:
    return os.environ['FEATURE_NAME']

@fixture
def api_stack_name(feature_name) -> str:
    return f"API{feature_name}"

@fixture
def db_stack_name(feature_name) -> str:
    return f"DB{feature_name}"

@fixture
def cognito_stack_name(feature_name) -> str:
    return f"Cognito{feature_name}"

@fixture
def event_stack_name(feature_name) -> str:
    return f"Event{feature_name}"


@fixture
def api_stack_outputs(api_stack_name: str) -> dict:
    api_stack = cfn_client.describe_stacks(StackName=api_stack_name)
    outputs = api_stack["Stacks"][0]["Outputs"]
    return {output["OutputKey"]: output["OutputValue"] for output in outputs}

@fixture
def cognito_stack_outputs(cognito_stack_name: str) -> dict:
    cognito_stack = cfn_client.describe_stacks(StackName=cognito_stack_name)
    outputs = cognito_stack["Stacks"][0]["Outputs"]
    return {output["OutputKey"]: output["OutputValue"] for output in outputs}

@fixture
def event_stack_outputs(event_stack_name: str) -> dict:
    event_stack = cfn_client.describe_stacks(StackName=event_stack_name)
    outputs = event_stack["Stacks"][0]["Outputs"]
    return {output["OutputKey"]: output["OutputValue"] for output in outputs}


@fixture
def app_root_url(api_stack_outputs: dict) -> str:
    return api_stack_outputs["RootUrl"]

@fixture
def get_restaurant_api_url(app_root_url: str) -> str:
    return f"{app_root_url}restaurants"

@fixture
def search_restaurant_api_url(get_restaurant_api_url: str) -> str:
    return f"{get_restaurant_api_url}/search"

@fixture
def order_api_url(app_root_url: str) -> str:
    return f"{app_root_url}orders"


@fixture
def cognito_user_pool_id(cognito_stack_outputs: dict) -> str:
    return cognito_stack_outputs["UserPoolId"]

@fixture
def cognito_server_user_pool_client_id(cognito_stack_outputs: dict) -> str:
    return cognito_stack_outputs["ServerUserPoolClientId"]


@fixture
def event_bus_arn(event_stack_outputs: dict) -> str:
    return event_stack_outputs["EventBusArn"]

@fixture
def restaurant_notification_topic_arn(event_stack_outputs: dict) -> str:
    return event_stack_outputs["RestaurantNotificationTopicArn"]

# -------------------
# common Gherkins steps

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
