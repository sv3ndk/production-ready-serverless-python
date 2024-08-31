from aws_cdk import (
    Stack,
    Fn,
    aws_cognito,
    aws_lambda,
    aws_apigateway,
    aws_lambda_python_alpha,
    aws_events,
    CfnOutput,
    Duration
)
from aws_cdk.aws_apigateway import StageOptions
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk.aws_ssm import StringParameter

from constructs import Construct


class ApiStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,

            service_name: str,
            feature_name: str,
            maturity_level: str,

            restaurants_table: Table,
            event_bus: aws_events.EventBus,
            cognito_user_pool: aws_cognito.UserPool,
            cognito_web_user_pool_client: aws_cognito.UserPoolClient,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = aws_apigateway.RestApi(
            scope=self,
            id=f"api{feature_name}",
            deploy_options=StageOptions(
                stage_name=feature_name
            )
        )

        api_logical_id = self.get_logical_id(api.node.default_child)

        def api_url(path: str = "/") -> str:
            return Fn.sub(f"https://${{{api_logical_id}}}.execute-api.${{AWS::Region}}.amazonaws.com/{feature_name}{path}")

        def ssm_params_path(suffix: str) -> str:
            """
            Returns the SSM parameter path for the given suffix.
            """
            return Fn.sub(f"arn:aws:ssm:${{AWS::Region}}:${{AWS::AccountId}}:parameter/{service_name}/shared_context/{maturity_level}{suffix}")

        cognito_authorizer = aws_apigateway.CognitoUserPoolsAuthorizer(
            scope=self,
            id="CognitoAuthorizer",
            cognito_user_pools=[cognito_user_pool],
        )

        # GET /restaurants
        # internal API: protected by IAM

        get_restaurants_fn = aws_lambda_python_alpha.PythonFunction(
            scope=self,
            id="get_restaurants",
            entry="functions/get_restaurants",
            index="get_restaurants.py",
            handler="handler",
            timeout=Duration.seconds(15),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "POWERTOOLS_SERVICE_NAME": service_name,
                "MATURITY_LEVEL": maturity_level,
                "TABLE_NAME": restaurants_table.table_name,
            }
        )
        restaurants_table.grant_read_data(get_restaurants_fn)
        get_restaurants_fn.role.add_to_principal_policy(
            PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    ssm_params_path("/get_restaurants/*")
                ],
                effect=Effect.ALLOW
            )
        )
        restaurants_api = api.root.add_resource('restaurants')
        restaurants_api.add_method(
            http_method='GET',
            integration=aws_apigateway.LambdaIntegration(get_restaurants_fn),
            authorization_type=aws_apigateway.AuthorizationType.IAM
        )

        # POST /restaurants/search
        # external API: protected by Cognito

        search_restaurants_fn = aws_lambda_python_alpha.PythonFunction(
            scope=self,
            id="search_restaurants",
            entry="functions/search_restaurants",
            index="search_restaurants.py",
            handler="handler",
            timeout=Duration.seconds(15),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "POWERTOOLS_SERVICE_NAME": service_name,
                "MATURITY_LEVEL": maturity_level,
                "TABLE_NAME": restaurants_table.table_name,
            }
        )
        search_restaurants_fn.role.add_to_principal_policy(
            PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    ssm_params_path("/search_restaurants/*")
                ],
                effect=Effect.ALLOW
            )
        )

        restaurants_table.grant_read_data(search_restaurants_fn)
        restaurants_api.add_resource('search').add_method(
            http_method='POST',
            integration=aws_apigateway.LambdaIntegration(search_restaurants_fn),
            authorization_type=aws_apigateway.AuthorizationType.COGNITO,
            authorizer=cognito_authorizer
        )

        # GET /
        # may access the internal API (via HTTP and signed requests with signature v4)

        get_index_fn = aws_lambda_python_alpha.PythonFunction(
            scope=self,
            id="get_index",
            entry="functions/get_index",
            index="get_index.py",
            handler="handler",
            timeout=Duration.seconds(15),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "POWERTOOLS_SERVICE_NAME": service_name,
                # we can't use the API Gateway resource here to know the URL because it would create a circular dependency
                # "RESTAURANTS_API_URL": Fn.sub(f"https://${{{api_logical_id}}}.execute-api.${{AWS::Region}}.amazonaws.com/{stage_name}/restaurants"),
                "RESTAURANTS_API_URL": api_url("/restaurants"),
                "ORDER_API_URL": api_url("/orders"),
                "COGNITO_USER_POOL_ID": cognito_user_pool.user_pool_id,
                "COGNITO_CLIENT_ID": cognito_web_user_pool_client.user_pool_client_id
            }
        )
        get_index_fn.role.add_to_principal_policy(
            PolicyStatement(
                actions=[ "execute-api:Invoke"],
                resources=[
                    Fn.sub(f"arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:${{{api_logical_id}}}/{feature_name}/GET/restaurants")
                ],
                effect=Effect.ALLOW
            )
        )
        api.root.add_method(
            "GET",
            aws_apigateway.LambdaIntegration(get_index_fn)
        )

        # ------
        # POST /orders

        place_order_fn = aws_lambda_python_alpha.PythonFunction(
            scope=self,
            id="place_order",
            entry="functions/place_order",
            index="place_order.py",
            handler="handler",
            timeout=Duration.seconds(5),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "POWERTOOLS_SERVICE_NAME": service_name,
                "MATURITY_LEVEL": maturity_level,
                "EVENT_BUS_NAME": event_bus.event_bus_name,
            }
        )
        event_bus.grant_put_events_to(place_order_fn)
        api.root.add_resource('orders').add_method(
            http_method='POST',
            integration=aws_apigateway.LambdaIntegration(place_order_fn),
            authorization_type=aws_apigateway.AuthorizationType.COGNITO,
            authorizer=cognito_authorizer
        )

        # ----------

        CfnOutput(
            scope=self,
            id="root_url",
            key="RootUrl",
            value=api_url()
        )

        StringParameter(
            scope=self,
            id="api_url",
            parameter_name=f"/{service_name}/{feature_name}/service_url",
            string_value=api_url()
        )
