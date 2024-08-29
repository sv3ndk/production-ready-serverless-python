#!/usr/bin/env python3
import aws_cdk as cdk
import os

from api_stack import ApiStack
from db_stack import DbStack
from cognito_stack import CognitoStack

app = cdk.App()

# determines the shared namespace for fetching the SSM parameters from: dev, test, acc or prod
maturity_level = os.getenv("MATURITY_LEVEL")

# name of feature for this environment (e.g. "add_get_restaurants")
feature_name = os.getenv("FEATURE_NAME")


db_stack = DbStack(
    app,
    construct_id=f"DB{feature_name}",
)

cognito_stack = CognitoStack(
    scope=app,
    construct_id=f"Cognito{feature_name}",
)

ApiStack(
    app,
    construct_id=f"API{feature_name}",
    service_name="production_ready_serverless",
    feature_name=feature_name,
    maturity_level=maturity_level,
    restaurants_table=db_stack.table,
    cognito_user_pool=cognito_stack.user_pool,
    cognito_web_user_pool_client=cognito_stack.web_user_pool_client,
    )

app.synth()
