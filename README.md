# Production ready serverless

Coding along while following the 
[Production ready serverless](https://school.theburningmonk.com/courses/production-ready-serverless-aug-2024-cdk)
course.

# Overview

* CDK deployment: [cdk/app.py](cdk/app.py)
* API (lambdas, behind a REST API on the API Gateway)
  * `/restaurants`: 
    * internal API listing all restaurants from DynamoDB
    * protected by IAM
  * `/restaurants/search`: 
    * search by attribute in DynamoDB (scans.. :( ))
    * protected by Cognito: simply checking if the user has a JWT token for the configured Cognito user pool
  * `/` : 
    * public HTML page 
    * which queries data from `/restaurants`, signing requests with sigv4.
    * is allowing to create/signin in users in the Cognito user pool, using SRP.
    * uses the Cognito JWT token to send requests to `/restaurants/search`

# Dev setup

```sh
python3.12 -m venv .venv-box
source .venv-box/bin/activate
pip install -r cdk/requirements.txt
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
