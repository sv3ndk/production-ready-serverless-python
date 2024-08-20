from aws_cdk import (
    Stack,
    aws_cognito
)
from aws_cdk.aws_cognito import StandardAttribute
from constructs import Construct


class CognitoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = aws_cognito.UserPool(
            scope=self,
            id="user_pool",
            self_sign_up_enabled=True,
            sign_in_case_sensitive=True,
            auto_verify=aws_cognito.AutoVerifiedAttrs(
                email=True
            ),
            sign_in_aliases=aws_cognito.SignInAliases(
                email=True
            ),
            password_policy=aws_cognito.PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=False,
                require_uppercase=False,
                require_symbols=False
            ),
            standard_attributes=aws_cognito.StandardAttributes(
                given_name=StandardAttribute(
                    required=True,
                    mutable=True
                ),
                family_name=StandardAttribute(
                    required=True,
                    mutable=True
                ),
                email=StandardAttribute(
                    required=True,
                    mutable=False
                )
            )
        )

        # used by the web app
        self.web_user_pool_client = aws_cognito.UserPoolClient(
            scope=self,
            id="web_user_pool_client",
            user_pool=self.user_pool,
            auth_flows=aws_cognito.AuthFlow(
                user_srp=True
            ),
            prevent_user_existence_errors=True
        )

        self.server_user_pool_client = aws_cognito.UserPoolClient(
            scope=self,
            id="server_user_pool_client",
            user_pool=self.user_pool,
            auth_flows=aws_cognito.AuthFlow(
                admin_user_password=True
            ),
            prevent_user_existence_errors=True
        )
