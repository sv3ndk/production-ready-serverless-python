# Production ready serverless

Coding along while following the 
[Production ready serverless](https://school.theburningmonk.com/courses/production-ready-serverless-aug-2024-cdk)
course.

# Overview

Status: Week 3 in progress

* CDK deployment: [cdk/app.py](cdk/app.py)

* REST API:
  * lambda functions exposed behing a REST API Gateway, handled with lambda power tools and pydantic data models
  * endpoints:
    * `/restaurants`: 
      * internal API listing all restaurants from DynamoDB
      * protected with IAM
    * `/restaurants/search`: 
      * search by attribute in DynamoDB 
      * protected with Cognito
    * `/orders`: 
      * used to post new orders
      * protected with Cognito
      * asynchronous processing: event is pushed to EventBridge, then processed by a lambda
    * `/` : 
      * public HTML page 
      * queries data from `/restaurants` on server side, signing requests with sigv4
      * allows users to register or sign in to the Cognito user pool, using SRP
      * uses the Cognito JWT token to send requests from the browser to `/restaurants/search`

* [Lambda Power Tools](https://docs.powertools.aws.dev/lambda/python/latest/) is used for REST request handling, 
  idempotency, event sourced event parsing and logging

* database: DynamoDB

* Tests: 
  * BDD style [integration tests](tests/integration/features) and [end-to-end tests](tests/end-to-end/features) 
    using pytest-bdd
  * Event-driven cases are validated by creating temporary SQS test queues to capture the events during the tests

# Dev setup

```sh
python3.12 -m venv .venv-box
source .venv-box/bin/activate
pip install -r cdk/requirements.txt
```

# Shared SSM parameters

In this project, SSM is used for the configuration shared across different deployments, following the convention:

```
/{SERVICE_NAME}/shared_context/{MATURITY_LEVEL}/..."
```

where:

* `SERVICE_NAME` is the name of the service, e.g. `production-ready-serverless`
* `MATURITY_LEVEL` is linked to the release life cycle, e.g. `dev`, `test`, `acc`, `prod`

Note that the `FEATURE_NAME`, used in the deployed stack name, is _not_ part of the SSM parameter path.

Those parameters are expected to be created before the deployment and their value is shared across all deployments 
having the same maturity level (each with a different feature name). 
This allows to share contextual information, like the URL of 3rd API,...

For dynamic configuration that should not be shared across deployments, e.g. feature flags,  we could use a 
convention similar to the following instead:

```
# (not currently implemented in this demo project)
/{SERVICE_NAME}/{FEATURE_NAME}/..."
```

# How to use

The `FEATURE_NAME` env variable is used to prefix the stack and API names.

Build and deploy:

```sh
MATURITY_LEVEL=dev \
FEATURE_NAME=feature-foo \
  cdk deploy \
  --all
```

Deployment delta:

```sh
MATURITY_LEVEL=dev \
FEATURE_NAME=feature-foo \
  cdk diff
```

Seed the DB:

```shell
MATURITY_LEVEL=dev \
FEATURE_NAME=feature-foo \
  python seed/seed_restaurants.py
```

See stack output for the app URL, then open it in a browser.

# Tests

Both the integration and end-to-end tests require resources to already be present in the AWS account.

The database should also have been seeded with the script above to match exactly the test expectations 
(TODO: automate this step).

Executing the tests requires to be authenticated with AWS.

Create a virtualenv with the required dependencies

```sh
pip install -r functions/get_index/requirements.txt
pip install -r tests/requirements.txt
````

## Integration tests

Integration tests are invoking the lambdas handlers directly. 
The `MATURITY_LEVEL` and `FEATURE_NAME` environment variables are used to retrieve AWS resources details.
 
```sh
MATURITY_LEVEL=dev \
FEATURE_NAME=feature-foo \
PYTHONPATH=src/functions/get_index:src/functions/get_restaurants:src/functions/search_restaurants \
  pytest tests/integration \
  -s \
  -v \
  --gherkin-terminal-reporter -v
```

## End-to-end tests

Integration tests are invoking the REST endpoints exposed via the API-gateway.

Temporary Cognito users are created and deleted during the tests.

```sh
PYTHONPATH=src/functions/place_order \
FEATURE_NAME=feature-foo \
  pytest tests/end-to-end \
  -s \
  -v \
  --gherkin-terminal-reporter -v
```

Add `-k` to run a specific test file, e.g.:

```sh
PYTHONPATH=src/functions/place_order \
FEATURE_NAME=feature-foo \
  pytest tests/end-to-end \
  -s \
  -v \
  --gherkin-terminal-reporter -v \
  -k test_orders_scenarios.py
```
