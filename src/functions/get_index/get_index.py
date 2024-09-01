from http import HTTPStatus

import boto3
import botocore.session
import datetime
import os
import jinja2
import requests
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response, content_types
from aws_lambda_powertools.utilities.typing import LambdaContext
from requests_aws4auth import AWS4Auth
from aws_lambda_powertools.logging import Logger

logger = Logger(log_uncaught_exceptions=True)
web_app = APIGatewayRestResolver(enable_validation=True)


RESTAURANTS_API_URL = os.getenv("RESTAURANTS_API_URL")
if not RESTAURANTS_API_URL:
    raise ValueError("RESTAURANTS_API_URL environment variable is not set")

ORDER_API_URL = os.getenv("ORDER_API_URL")
if not ORDER_API_URL:
    raise ValueError("ORDER_API_URL environment variable is not set")

COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
if not COGNITO_USER_POOL_ID:
    raise ValueError("COGNITO_USER_POOL_ID environment variable is not set")

COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
if not COGNITO_CLIENT_ID:
    raise ValueError("COGNITO_CLIENT_ID environment variable is not set")

with open(os.path.join(os.path.dirname(__file__), "index.html")) as f:
    index_html_template = f.read()

aws_region = boto3.session.Session().region_name


def all_restaurants() -> list[dict]:
    auth = AWS4Auth(
        refreshable_credentials=botocore.session.Session().get_credentials(),
        service='execute-api',
        region=aws_region
    )
    response = requests.get(RESTAURANTS_API_URL, auth=auth)
    response.raise_for_status()
    return response.json()


@web_app.get("/")
def get_index():
    restaurants = all_restaurants()
    logger.info(f"restaurants: {restaurants}")
    day_of_week = datetime.datetime.today().strftime("%A")

    template = jinja2.Template(source=index_html_template)
    index_html = template.render(
        dayOfWeek=day_of_week,
        restaurants=restaurants,
        searchUrl=f"{RESTAURANTS_API_URL}/search",
        orderUrl=ORDER_API_URL,
        awsRegion=aws_region,
        cognitoUserPoolId=COGNITO_USER_POOL_ID,
        cognitoClientId=COGNITO_CLIENT_ID
    )

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.TEXT_HTML,
        body=index_html
    )

def handler(event: dict, context: LambdaContext) -> dict:
    return web_app.resolve(event, context)
