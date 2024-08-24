# Production ready serverless

Coding along while following the 
[Production ready serverless](https://school.theburningmonk.com/courses/production-ready-serverless-aug-2024-cdk)
course.

# Overview

Status: Week 1 completed

* CDK deployment: [cdk/app.py](cdk/app.py)
* API (lambdas, behind a REST API on the API Gateway)
  * `/restaurants`: 
    * internal API listing all restaurants from DynamoDB
    * protected by IAM
  * `/restaurants/search`: 
    * search by attribute in DynamoDB 
    * protected by Cognito: simply checking if the user has a JWT token for the configured Cognito user pool
  * `/` : 
    * public HTML page 
    * queries data from `/restaurants` on server side, signing requests with sigv4
    * is allowing users to create/sign in the Cognito user pool, using SRP
    * uses the Cognito JWT token to send requests from the browser to `/restaurants/search`

# Dev setup

```sh
python3.12 -m venv .venv-box
source .venv-box/bin/activate
pip install -r cdk/requirements.txt
```

# Launch integration tests

```sh
# TODO: we should use 2 venv here
pip install -r tests/integration/requirements.txt

pytest tests/integration -s -v
```

# How to use

The `STAGE_NAME` env variable is used to prefix the stack and API names

Build and deploy:

```sh
STAGE_NAME=feature-foo cdk deploy --all
STAGE_NAME=feature-foo cdk diff
...
```

Seed the DB:

```shell
python seed/seed_restaurants.py --db-stack-name DB-svend
```

See stack output for the app URL, then open it in a browser.


<img id="logo" src="https://d2qt42rcwzspd6.cloudfront.net/manning/big-mouth.png">