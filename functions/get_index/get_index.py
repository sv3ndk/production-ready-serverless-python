import boto3
import botocore.session
import datetime
import os
import jinja2
import requests
from requests_aws4auth import AWS4Auth

RESTAURANTS_API_URL = os.getenv("RESTAURANTS_API_URL")
if not RESTAURANTS_API_URL:
    raise ValueError("RESTAURANTS_API_URL environment variable is not set")

index_html_template = open("index.html").read()

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


def handler(event, context):
    restaurants = all_restaurants()
    print(f"restaurants: {restaurants}")
    day_of_week = datetime.datetime.today().strftime("%A")

    template = jinja2.Template(source=index_html_template)
    index_html = template.render(
        dayOfWeek=day_of_week,
        restaurants=restaurants
    )

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': index_html
    }
