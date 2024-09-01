import json
from contextlib import contextmanager

import boto3
from attr import dataclass
from faker import Faker

sqs_client = boto3.client("sqs")
sns_client = boto3.client("sns")

@contextmanager
def temporary_queue():
    """
    Create a temporary SQS queue
    """
    queue_name = f"2e2tests_orders_{Faker().uuid4().replace('-', '')[:10]}"
    print(f"creating sqs queue {queue_name}")
    queue_url = sqs_client.create_queue(QueueName=queue_name)["QueueUrl"]

    yield queue_url

    print(f"deleting sqs queue {queue_name}")
    sqs_client.delete_queue(QueueUrl=queue_url)


@contextmanager
def temporary_queue_subscribed_to_sns(topic_arn: str):
    """
    Create a temporary SQS queue and subscribe it to a SNS topic
    """

    with temporary_queue() as queue_url:
        print(f"subscribing queue {queue_url} to topic {topic_arn}")

        queue_arn = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["QueueArn"]
        )["Attributes"]["QueueArn"]

        sqs_client.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={
                "Policy": json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "sns.amazonaws.com"
                            },
                            "Action": "sqs:SendMessage",
                            "Resource": queue_arn,
                            "Condition": {
                                "ArnEquals": {
                                    "aws:SourceArn": topic_arn
                                }
                            }
                        }
                    ]
                })
            }
        )

        subscription_arn = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=queue_arn,
            Attributes={"RawMessageDelivery": "false"}
        )["SubscriptionArn"]

        yield queue_url

        print(f"unsubscribing queue {queue_url}")
        sns_client.unsubscribe(SubscriptionArn=subscription_arn)


@dataclass
class DebugNotificationMessage:
    sourceType: str
    source: str
    message: dict

def read_message_from_sqs(queue_url: str) -> list[DebugNotificationMessage]:
    """
    Read and parse messages from a SQS queue
    """

    receive_response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=10
    )
    assert "Messages" in receive_response

    orders = []
    for message in receive_response["Messages"]:
        body = json.loads(message["Body"])

        if "TopicArn" in body:
            sourceType = "sns"
            source = body["TopicArn"]
        else:
            sourceType = "???"
            source = "???"

        orders.append(DebugNotificationMessage(
            sourceType=sourceType,
            source=source,
            message=json.loads(body["Message"])
        ))

    return orders
