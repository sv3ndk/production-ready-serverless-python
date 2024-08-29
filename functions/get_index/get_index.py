import boto3
import botocore.session
import datetime
import os
import jinja2
import requests
from requests_aws4auth import AWS4Auth
from aws_lambda_powertools.logging import Logger

logger = Logger(log_uncaught_exceptions=True)


RESTAURANTS_API_URL = os.getenv("RESTAURANTS_API_URL")
if not RESTAURANTS_API_URL:
    raise ValueError("RESTAURANTS_API_URL environment variable is not set")

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


def handler(event, context) -> dict:
    restaurants = all_restaurants()
    logger.info(f"restaurants: {restaurants}")
    day_of_week = datetime.datetime.today().strftime("%A")

    template = jinja2.Template(source=index_html_template)
    index_html = template.render(
        dayOfWeek=day_of_week,
        restaurants=restaurants,
        searchUrl=f"{RESTAURANTS_API_URL}/search",
        awsRegion=aws_region,
        cognitoUserPoolId=COGNITO_USER_POOL_ID,
        cognitoClientId=COGNITO_CLIENT_ID
    )

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': index_html
    }
