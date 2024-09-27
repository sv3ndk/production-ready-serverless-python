from constructs import Construct
from aws_cdk import aws_lambda as lambda_
from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonFunctionProps


def traced_python_function(scope: Construct, id: str, props: PythonFunctionProps) -> PythonFunction:
    props2 = {
        k: v
        for k, v in props.__dict__["_values"].items()
    }

    props2["tracing"] = lambda_.Tracing.ACTIVE

    if "memory_size" not in props2:
        props2["memory_size"] = 1024

    return PythonFunction(scope, id, **props2)