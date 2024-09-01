import os
from pytest import fixture
import boto3


cfn_client = boto3.client('cloudformation')

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
def db_stack_outputs(db_stack_name: str) -> dict:
    db_stack = cfn_client.describe_stacks(StackName=db_stack_name)
    outputs = db_stack["Stacks"][0]["Outputs"]
    return {output["OutputKey"]: output["OutputValue"] for output in outputs}


@fixture
def app_root_url(api_stack_outputs: dict) -> str:
    return api_stack_outputs["RootUrl"]

@fixture
def app_restaurant_url(app_root_url: str) -> str:
    return f"{app_root_url}/restaurants"

@fixture
def restaurant_table_name(db_stack_outputs: dict) -> str:
    return db_stack_outputs["RestaurantsTableName"]

@fixture
def app_order_url(app_root_url: str) -> str:
    return f"{app_root_url}/orders"

@fixture
def cognito_user_pool_id(cognito_stack_outputs: dict) -> str:
    return cognito_stack_outputs["UserPoolId"]

@fixture
def cognito_web_user_pool_client_id(cognito_stack_outputs: dict) -> str:
    return cognito_stack_outputs["WebUserPoolClientId"]
