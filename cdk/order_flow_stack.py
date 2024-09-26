from aws_cdk import (
    Stack,
    aws_events,
    aws_sns,
    aws_stepfunctions
)
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_stepfunctions import DefinitionBody
from constructs import Construct


class OrderFlowStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,

            orders_table: Table,
            event_bus: aws_events.EventBus,
            restaurant_notification_topic: aws_sns.Topic,
            user_notification_topic: aws_sns.Topic,

            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # This flow is not triggered anywhere, it's just a demo of how to implement the order use case with a
        # step functions, and without any lambda.
        # in the context of the course, this is triggered manually.
        self.flow = aws_stepfunctions.StateMachine(
            scope=self,
            id="OrderFlowStateMachine",
            definition_body=DefinitionBody.from_file("state_machines/order_flow.asl.json"),
            definition_substitutions={
                "ORDERS_TABLE_NAME": orders_table.table_name,
                "EVENT_BUS_NAME": event_bus.event_bus_name,
                "RESTAURANT_NOTIFICATION_TOPIC_ARN": restaurant_notification_topic.topic_arn,
                "USER_NOTIFICATION_TOPIC_ARN": user_notification_topic.topic_arn
            }
        )
        orders_table.grant_write_data(self.flow)
        event_bus.grant_put_events_to(self.flow)
        restaurant_notification_topic.grant_publish(self.flow)
        user_notification_topic.grant_publish(self.flow)
