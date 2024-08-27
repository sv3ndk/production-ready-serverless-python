#!/usr/bin/env python3
import aws_cdk as cdk
import os

from api_stack import ApiStack
from db_stack import DbStack
from cognito_stack import CognitoStack

app = cdk.App()

stage_name = os.getenv("STAGE_NAME") or "dev"

db_stack = DbStack(
    app,
    construct_id=f"DB-{stage_name}",
)

cognito_stack = CognitoStack(
    scope=app,
    construct_id=f"Cognito-{stage_name}",
)

ApiStack(
    app,
    construct_id=f"API-{stage_name}",
    service_name="production-ready-serverless",
    stage_name=stage_name,
    restaurants_table=db_stack.table,
    cognito_user_pool=cognito_stack.user_pool,
    cognito_web_user_pool_client=cognito_stack.web_user_pool_client,
    )

app.synth()
