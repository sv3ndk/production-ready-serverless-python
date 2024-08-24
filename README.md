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
* Test:
  * BDD style [integration tests](tests/integration/features) using pytest-bdd


# Dev setup

```sh
python3.12 -m venv .venv-box
source .venv-box/bin/activate
pip install -r cdk/requirements.txt
```

# How to use

The `STAGE_NAME` env variable is used to prefix the stack and API names.

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

# Launch integration tests

Integration test are invoking the lambdas handlers directly, relying on resources created in the AWS account
by the CDK stack. Execution the integration tests requires to be authenticated with AWS. 

The `STAGE_NAME` environment variable is used to retrieve those resources details when running the tests.

Make sure the database is seeded with the script above to match exactly the test expectations (TODO: automate this step).

```sh
# create a virtualenv with the required dependencies:
pip install -r functions/get_index/requirements.txt
pip install -r tests/integration/requirements.txt

STAGE_NAME=feature-foo PYTHONPATH=functions/get_index:functions/get_restaurants:functions/search_restaurants pytest tests/integration -s -v --gherkin-terminal-reporter -v
```
