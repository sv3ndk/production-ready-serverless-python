from aws_cdk import (
    Stack,
    aws_dynamodb,
    CfnOutput
)
from constructs import Construct


class DbStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.table = aws_dynamodb.Table(
            scope=self,
            id="restaurants",
            partition_key=aws_dynamodb.Attribute(
                name="name",
                type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
        )

        self.orders = aws_dynamodb.Table(
            scope=self,
            id="orders",
            partition_key=aws_dynamodb.Attribute(
                name="id",
                type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
        )

        self.idempotency_table = aws_dynamodb.Table(
            scope=self,
            id="idempotency",
            partition_key=aws_dynamodb.Attribute(
                name="id",
                type=aws_dynamodb.AttributeType.STRING
            ),
            # name of the attribute that stores the time-to-live value:
            time_to_live_attribute="exiration",
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
        )

        CfnOutput(
            scope=self,
            id="restaurants_table_name",
            key="RestaurantsTableName",
            value=self.table.table_name
        )
