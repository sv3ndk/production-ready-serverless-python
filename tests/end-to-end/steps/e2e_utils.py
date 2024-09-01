import json
import time
from contextlib import contextmanager
import datetime as dt

import boto3
from attr import dataclass
from faker import Faker

sqs_client = boto3.client("sqs")
sns_client = boto3.client("sns")
eventbridge_client = boto3.client("events")

@dataclass
class TemporaryQueue:
    url: str
    arn: str


@contextmanager
def temporary_queue(trusted_service: str):
    """
    Create a temporary SQS queue
    """
    queue_name = f"2e2_test_{Faker().uuid4().replace('-', '')[:10]}"
    print(f"creating sqs queue {queue_name}")
    queue_url = sqs_client.create_queue(QueueName=queue_name)["QueueUrl"]

    queue_arn = sqs_client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["QueueArn"]
    )["Attributes"]["QueueArn"]

    sqs_client.set_queue_attributes(
        QueueUrl=queue_url,

        # TODO: we should restrict to one source SQS/EventBridge arn here...
        Attributes={
            "Policy": json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": trusted_service
                        },
                        "Action": "sqs:SendMessage",
                        "Resource": queue_arn,
                    }
                ]
            })
        }
    )

    yield TemporaryQueue(url=queue_url, arn=queue_arn)

    print(f"deleting sqs queue {queue_name}")
    sqs_client.delete_queue(QueueUrl=queue_url)


@contextmanager
def temporary_queue_subscribed_to_sns(topic_arn: str):
    """
    Create a temporary SQS queue and subscribe it to a SNS topic
    """

    with temporary_queue(trusted_service="sns.amazonaws.com") as tmp_queue:
        print(f"subscribing queue {tmp_queue.url} to topic {topic_arn}")

        subscription_arn = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=tmp_queue.arn,
            Attributes={"RawMessageDelivery": "false"}
        )["SubscriptionArn"]

        yield tmp_queue

        print(f"unsubscribing queue {tmp_queue.url} from topic {topic_arn}")
        sns_client.unsubscribe(SubscriptionArn=subscription_arn)


@contextmanager
def temporary_queue_subscribed_to_event_bus(event_bus_name: str, event_pattern: dict):
    """
    Create a temporary SQS queue and subscribe it to an EventBridge event bus
    """

    with temporary_queue(trusted_service='events.amazonaws.com') as tmp_queue:
        print(f"subscribing queue {tmp_queue.url} to event bus {event_bus_name}")

        rule_name = f"e2e_test_rule-{Faker().uuid4()}"
        eventbridge_client.put_rule(
            Name=rule_name,
            EventBusName=event_bus_name,
            EventPattern=json.dumps(event_pattern)
        )

        eventbridge_client.put_targets(
            Rule=rule_name,
            EventBusName=event_bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": tmp_queue.arn,
                }
            ]
        )

        while (status := eventbridge_client.describe_rule(Name=rule_name, EventBusName=event_bus_name)['State']) != 'ENABLED':
            print(f"waiting for subscription: current status: {status}")
            time.sleep(1)

        # not sure why, but even when marked as "ENABLED", we sometimes miss the first events
        # => wait a bit more, which likely makes the test flaky and unnecessarily slow :(
        time.sleep(10)

        yield tmp_queue

        print(f"deleting rule {rule_name}")
        eventbridge_client.remove_targets(Rule=rule_name, EventBusName=event_bus_name, Ids=["1"])
        eventbridge_client.delete_rule(Name=rule_name, EventBusName=event_bus_name)


def read_sqs_messages(queue_url: str, expected: int, timeout_seconds: int) -> list[dict]:
    """
    Tries to read the expected number of messages from an SQS queue by repeatedly polling it
    """

    orders = []
    start = dt.datetime.now()

    while (dt.datetime.now() - start).seconds < timeout_seconds and len(orders) < expected:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=timeout_seconds
        )
        print(f"received {len(response.get('Messages', []))} messages from {queue_url}")

        if "Messages" in response:
            orders.extend(
                json.loads(message["Body"])
                for message in response["Messages"]
            )

    return  orders
