# Production ready serverless

Coding along while following the 
[Production ready serverless](https://school.theburningmonk.com/courses/production-ready-serverless-aug-2024-cdk)
course.

# Overview

Status: Week 3 in progress

* CDK deployment: [cdk/app.py](cdk/app.py)

* REST API:
  * lambda functions with lambda-power-tools handling and pydantic data models, exposed via a REST API Gateway
  * endpoints:
    * `/restaurants`: 
      * internal API listing all restaurants from DynamoDB
      * protected by IAM
    * `/restaurants/search`: 
      * search by attribute in DynamoDB 
      * protected by Cognito: simply checking if the user has a JWT token for the configured Cognito user pool
    * `/` : 
      * public HTML page 
      * queries data from `/restaurants` on server side, signing requests with sigv4
      * allows users to register or sign in to the Cognito user pool, using SRP
      * uses the Cognito JWT token to send requests from the browser to `/restaurants/search`

* database: DynamoDB

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
FEATURE_NAME=feature-foo \
  pytest tests/end-to-end \
  -s \
  -v \
  --gherkin-terminal-reporter -v
```

# Shared SSM parameters

In this project, SSM is used for the configuration shared across different deployments, following the convention:

```
/{SERVICE_NAME}/shared_context/{MATURITY_LEVEL}/..."
```

where:

* `SERVICE_NAME` is the name of the service, e.g. `production-ready-serverless`
* `MATURITY_LEVEL` is linked to the release life cycle, e.g. `dev`, `test`, `acc`, `prod`

Those parameters are expected to be created before the deployment.

This allows to share contextual information, like the URL of 3rd API, across all environments of a given maturity level.

For dynamic configuration that should not be shared across deployments, e.g. feature flags, 
we could use a convention similar to the following instead:

```
# (not currently implemented in this demo project)
/{SERVICE_NAME}/{FEATURE_NAME}/..."
```
