from aws_cdk import (
    Stack,
    Fn,
    aws_lambda,
    aws_apigateway,
    aws_lambda_python_alpha,
    aws_cognito
)
from aws_cdk.aws_apigateway import StageOptions
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_iam import PolicyStatement, Effect

from constructs import Construct


class ApiStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            stage_name: str,
            restaurants_table: Table,
            cognito_user_pool: aws_cognito.UserPool,
            cognito_web_user_pool_client: aws_cognito.UserPoolClient,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = aws_apigateway.RestApi(
            scope=self,
            id=f"{stage_name}-api",
            deploy_options=StageOptions(
                stage_name=stage_name
            )
        )

        api_logical_id = self.get_logical_id(api.node.default_child)

        # GET /restaurants
        # internal API: protected by IAM

        get_restaurants_fn = aws_lambda.Function(
            scope=self,
            id="get_restaurants",
            handler="get_restaurants.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset("functions/get_restaurants"),
            environment={
                "TABLE_NAME": restaurants_table.table_name,
                "RESULT_LIMIT": "10"
            }
        )
        restaurants_table.grant_read_data(get_restaurants_fn)
        restaurants_api = api.root.add_resource('restaurants')
        restaurants_api.add_method(
            http_method='GET',
            integration=aws_apigateway.LambdaIntegration(get_restaurants_fn),
            authorization_type=aws_apigateway.AuthorizationType.IAM
        )

        # POST /restaurants/search
        # external API: protected by Cognito

        search_restaurants_fn = aws_lambda.Function(
            scope=self,
            id="search_restaurants",
            handler="search_restaurants.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset("functions/search_restaurants"),
            environment={
                "TABLE_NAME": restaurants_table.table_name,
                "RESULT_LIMIT": "10"
            },
        )
        restaurants_table.grant_read_data(search_restaurants_fn)
        restaurants_api.add_resource('search').add_method(
            http_method='POST',
            integration=aws_apigateway.LambdaIntegration(search_restaurants_fn),
            authorizer=aws_apigateway.CognitoUserPoolsAuthorizer(
                scope=self,
                id="CognitoAuthorizer",
                cognito_user_pools=[cognito_user_pool],
            ),
        )

        # GET /
        # may access the internal API (via HTTP and signed requests with signature v4)

        get_index_fn = aws_lambda_python_alpha.PythonFunction(
            scope=self,
            id="get_index",
            entry="functions/get_index",
            index="get_index.py",
            handler="handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "TABLE_NAME": restaurants_table.table_name,
                # we can't use the API Gateway resource here to know the URL because it would create a circular dependency
                "RESTAURANTS_API_URL": Fn.sub(f"https://${{{api_logical_id}}}.execute-api.${{AWS::Region}}.amazonaws.com/{stage_name}/restaurants"),
                "COGNITO_USER_POOL_ID": cognito_user_pool.user_pool_id,
                "COGNITO_CLIENT_ID": cognito_web_user_pool_client.user_pool_client_id
            }
        )
        get_index_fn.role.add_to_principal_policy(
            PolicyStatement(
                actions=[ "execute-api:Invoke"],
                resources=[
                    Fn.sub(f"arn:aws:execute-api:${{AWS::Region}}:${{AWS::AccountId}}:${{{api_logical_id}}}/{stage_name}/GET/restaurants")
                ],
                effect=Effect.ALLOW
            )
        )
        api.root.add_method(
            "GET",
            aws_apigateway.LambdaIntegration(get_index_fn)
        )
