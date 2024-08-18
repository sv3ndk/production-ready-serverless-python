# Production ready serverless

Coding along while following the 
[Production ready serverless](https://school.theburningmonk.com/courses/production-ready-serverless-aug-2024-cdk)
course.

# Overview

* CDK deployment: [cdk/app.py](cdk/app.py)
* `/restaurants`: 
  * internal API listing restaurants from DynamoDB,
  * implemented as a lambda behind an API Gateway
  * protected by IAM
* `/` : 
  * public HTML page 
  * served by a lambda behind an API Gateway
  * which queries data from `/restaurants`, signing requests with sigv4.  

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

See stack output for the app URL.
