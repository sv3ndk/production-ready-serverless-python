from aws_cdk import (
    Stack,
    aws_events,
    aws_sqs,
    aws_sns,
    aws_lambda_python_alpha,
    Duration,
    aws_lambda,
    aws_cloudwatch,
    aws_cloudwatch_actions,
    aws_events_targets,
    CfnOutput
)
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_events import EventPattern
from aws_cdk.aws_lambda_destinations import SqsDestination
from constructs import Construct


class EventStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,

            service_name: str,
            feature_name: str,
            maturity_level: str,
            idempotency_table: Table,

            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.event_bus = aws_events.EventBus(
            scope=self,
            id="OrderEventBus"
        )
        self.restaurant_notification_topic = aws_sns.Topic(
            scope=self,
            id="RestaurantNotificationTopic",
        )
        restaurant_notification_error_queue = aws_sqs.Queue(
            scope=self,
            id="RestaurantNotificationErrorQueue"
        )
        alarm_topic = aws_sns.Topic(
            scope=self,
            id="AlarmTopic"
        )

        notify_restaurant_fn = aws_lambda_python_alpha.PythonFunction(
            scope=self,
            id="notify_restaurant",
            entry="src/functions/notify_restaurant",
            index="notify_restaurant.py",
            handler="handler",
            # CDK automatically grants the necessary IAM permissions to deliver failed messages to the error queue
            on_failure=SqsDestination(queue=restaurant_notification_error_queue),
            timeout=Duration.seconds(5),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "POWERTOOLS_SERVICE_NAME": service_name,
                "MATURITY_LEVEL": maturity_level,
                "EVENT_BUS_NAME": self.event_bus.event_bus_name,
                "TOPIC_ARN": self.restaurant_notification_topic.topic_arn,
                "IDEMPOTENCY_TABLE_NAME": idempotency_table.table_name
            }
        )
        self.event_bus.grant_put_events_to(notify_restaurant_fn)
        self.restaurant_notification_topic.grant_publish(notify_restaurant_fn)
        idempotency_table.grant_read_write_data(notify_restaurant_fn)

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

        on_failure_alarm = aws_cloudwatch.Alarm(
            scope=self,
            id="OnFailureQueueAlarm",
            # alarm_name=f"[{maturity_level}][NotifyRestaurant function] Failed events detected in OnFailure destination",
            metric=restaurant_notification_error_queue.metric_approximate_number_of_messages_visible(),
            comparison_operator=aws_cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=0,
            evaluation_periods=1,
            treat_missing_data=aws_cloudwatch.TreatMissingData.NOT_BREACHING
        )
        on_failure_alarm.add_alarm_action(aws_cloudwatch_actions.SnsAction(alarm_topic))

        destination_delivery_alarm = aws_cloudwatch.Alarm(
            scope=self,
            id="DestinationDeliveryFailuresAlarm",
            # alarm_name=f"[{maturity_level}][NotifyRestaurant function] Failed to deliver failed events to OnFailure destination",
            metric=notify_restaurant_fn.metric("DestinationDeliveryFailures"),
            comparison_operator=aws_cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=0,
            evaluation_periods=1,
            treat_missing_data=aws_cloudwatch.TreatMissingData.NOT_BREACHING
        )
        destination_delivery_alarm.add_alarm_action(aws_cloudwatch_actions.SnsAction(alarm_topic))


        CfnOutput(
            scope=self,
            id="EventBusArn",
            value=self.event_bus.event_bus_arn
        )
        CfnOutput(
            scope=self,
            id="EventBusName",
            value=self.event_bus.event_bus_name
        )
        CfnOutput(
            scope=self,
            id="RestaurantNotificationTopicArn",
            value=self.restaurant_notification_topic.topic_arn
        )
