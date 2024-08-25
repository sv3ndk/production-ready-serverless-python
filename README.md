# Production ready serverless

Coding along while following the 
[Production ready serverless](https://school.theburningmonk.com/courses/production-ready-serverless-aug-2024-cdk)
course.

# Overview

Status: Week 2 in-progress

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

* Test: BDD style [integration tests](tests/integration/features) and [end-to-end tests](tests/end-to-end/features) 
  using pytest-bdd

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
STAGE_NAME=feature-foo python seed/seed_restaurants.py
```

See stack output for the app URL, then open it in a browser.

# Tests

Both the integration and end-to-end tests require resources to already be present in the AWS account.

The database should also have been seeded with the script above to match exactly the test expectations 
(TODO: automate this step).

The `STAGE_NAME` environment variable is used to retrieve those resources details when running the tests.

Executing the tests requires to be authenticated with AWS.

Create a virtualenv with the required dependencies

```sh
pip install -r functions/get_index/requirements.txt
pip install -r tests/requirements.txt
````

## Integration tests

Integration tests are invoking the lambdas handlers directly, relying on resources present in the AWS account. 
 
```sh
STAGE_NAME=feature-foo \
PYTHONPATH=functions/get_index:functions/get_restaurants:functions/search_restaurants \
  pytest tests/integration \
  -s \
  -v \
  --gherkin-terminal-reporter -v
```

## End-to-end tests

Integration tests are invoking the REST endpoints exposed via the API-gateway.

Temporary Cognito users are created and deleted during the tests.

```sh
STAGE_NAME=feature-foo \
  pytest tests/end-to-end \
  -s \
  -v \
  --gherkin-terminal-reporter -v
```
