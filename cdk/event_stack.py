from aws_cdk import (
    Stack,
    aws_events,
    aws_sns, aws_lambda_python_alpha, Duration, aws_lambda, aws_events_targets
)
from aws_cdk.aws_events import EventPattern
from constructs import Construct


class EventStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,

            service_name: str,
            maturity_level: str,

            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.event_bus = aws_events.EventBus(
            scope=self,
            id="OrderEventBus"
        )

        self.topic = aws_sns.Topic(
            scope=self,
            id="RestaurantNotificationTopic",
            topic_name="RestaurantNotificationTopic"
        )

        notify_restaurant_fn = aws_lambda_python_alpha.PythonFunction(
            scope=self,
            id="notify_restaurant",
            entry="functions/notify_restaurant",
            index="notify_restaurant.py",
            handler="handler",
            timeout=Duration.seconds(5),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "POWERTOOLS_SERVICE_NAME": service_name,
                "MATURITY_LEVEL": maturity_level,
                "EVENT_BUS_NAME": self.event_bus.event_bus_name,
                "TOPIC_ARN": self.topic.topic_arn
            }
        )
        self.event_bus.grant_put_events_to(notify_restaurant_fn)
        self.topic.grant_publish(notify_restaurant_fn)

        rule = aws_events.Rule(
            scope=self,
            id="OrderPlacedRule",
            event_bus=self.event_bus,
            event_pattern=EventPattern(
                source=["big-mouth"],
                detail_type=["order_placed"]
            )
        )
        rule.add_target(target=aws_events_targets.LambdaFunction(handler=notify_restaurant_fn))
