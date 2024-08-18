import boto3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--db-stack-name", required=True)

args = parser.parse_args()
db_stack_name = args.db_stack_name

cfn_client = boto3.client('cloudformation')


def restaurant_table_name():
    db_stack = cfn_client.describe_stacks(StackName=db_stack_name)
    outputs = db_stack["Stacks"][0]["Outputs"]
    for output in outputs:
        if output["OutputKey"] == "RestaurantsTableName":
            return output["OutputValue"]

    raise ValueError("RestaurantsTableName not found in stack outputs")

restaurants = [
    {
        "name": "Fangtasia",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/fangtasia.png",
        "themes": ["true blood"]
    },
    {
        "name": "Shoney's",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/shoney's.png",
        "themes": ["cartoon", "rick and morty"]
    },
    {
        "name": "Freddy's BBQ Joint",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/freddy's+bbq+joint.png",
        "themes": ["netflix", "house of cards"]
    },
    {
        "name": "Pizza Planet",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/pizza+planet.png",
        "themes": ["netflix", "toy story"]
    },
    {
        "name": "Leaky Cauldron",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/leaky+cauldron.png",
        "themes": ["movie", "harry potter"]
    },
    {
        "name": "Lil' Bits",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/lil+bits.png",
        "themes": ["cartoon", "rick and morty"]
    },
    {
        "name": "Fancy Eats",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/fancy+eats.png",
        "themes": ["cartoon", "rick and morty"]
    },
    {
        "name": "Don Cuco",
        "image": "https://d2qt42rcwzspd6.cloudfront.net/manning/don%20cuco.png",
        "themes": ["cartoon", "rick and morty"]
    },
]

dynamo_resource = boto3.resource('dynamodb')
table_name = restaurant_table_name()
restaurant_table_client = dynamo_resource.Table(table_name)

with restaurant_table_client.batch_writer() as batch:
    for restaurant in restaurants:
        batch.put_item(Item=restaurant)