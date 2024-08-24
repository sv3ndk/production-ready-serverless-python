import os
from pytest import fixture
import boto3


cfn_client = boto3.client('cloudformation')


@fixture
def stage_name() -> str:
    return os.environ['STAGE_NAME']

@fixture
def api_stack_name(stage_name) -> str:
    return f"API-{stage_name}"

@fixture
def aws_region() -> str:
    return boto3.session.Session().region_name

@fixture
def cognito_stack_name(stage_name) -> str:
    return f"Cognito-{stage_name}"


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
def app_root_url(api_stack_outputs: dict) -> str:
    return api_stack_outputs["RootUrl"]

@fixture
def app_restaurant_url(app_root_url: str) -> str:
    return f"{app_root_url}restaurants"

@fixture
def search_restaurant_url(app_restaurant_url: str) -> str:
    return f"{app_restaurant_url}/search"

@fixture
def cognito_user_pool_id(cognito_stack_outputs: dict) -> str:
    return cognito_stack_outputs["UserPoolId"]

@fixture
def cognito_server_user_pool_client_id(cognito_stack_outputs: dict) -> str:
    return cognito_stack_outputs["ServerUserPoolClientId"]
