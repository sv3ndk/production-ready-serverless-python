#!/usr/bin/env python3
import aws_cdk as cdk
import os

from api_stack import ApiStack
from order_flow_stack import OrderFlowStack
from db_stack import DbStack
from cognito_stack import CognitoStack
from event_stack import EventStack

app = cdk.App()

service_name = "production_ready_serverless"

maturity_level = os.getenv("MATURITY_LEVEL")
assert maturity_level in ["dev", "test", "acc", "prod"], f"Invalid maturity level: {maturity_level}"

feature_name = os.getenv("FEATURE_NAME")
assert feature_name, "FEATURE_NAME environment variable must be set"

db_stack = DbStack(
    app,
    construct_id=f"DB{feature_name}",
)

cognito_stack = CognitoStack(
    scope=app,
    construct_id=f"Cognito{feature_name}",
)

event_stack = EventStack(
    scope=app,
    construct_id=f"Event{feature_name}",
    service_name=service_name,
    feature_name=feature_name,
    maturity_level=maturity_level,
    idempotency_table=db_stack.idempotency_table,
)

order_flow_stack = OrderFlowStack(
    app,
    construct_id=f"OrderFlow{feature_name}",
    orders_table=db_stack.table,
    event_bus=event_stack.event_bus,
    restaurant_notification_topic=event_stack.restaurant_notification_topic,
    user_notification_topic=event_stack.user_notification_topic,
)

ApiStack(
    app,
    construct_id=f"API{feature_name}",
    service_name=service_name,
    feature_name=feature_name,
    maturity_level=maturity_level,
    restaurants_table=db_stack.table,
    event_bus=event_stack.event_bus,
    cognito_user_pool=cognito_stack.user_pool,
    cognito_web_user_pool_client=cognito_stack.web_user_pool_client,
    )

app.synth()
