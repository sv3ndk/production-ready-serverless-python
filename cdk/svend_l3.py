from constructs import Construct
from aws_cdk import aws_lambda as lambda_
from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonFunctionProps


# class TracedPythonFunction(Construct):
#     def __init__(self, scope: Construct, id: str, props: PythonFunctionProps) -> None:
#         super().__init__(scope, id)
#
#         props2 = {
#             k: v
#             for k, v in props.__dict__["_values"].items()
#         }
#
#         props2["tracing"] = lambda_.Tracing.ACTIVE
#
#         self.lambda_function = PythonFunction(self, "Traced", **props2)
#
#     def function(self) -> PythonFunction:
#         return self.lambda_function

# remove the class, make it a function that returns the PythonFunction

def traced_python_function(scope: Construct, id: str, props: PythonFunctionProps) -> PythonFunction:
    props2 = {
        k: v
        for k, v in props.__dict__["_values"].items()
    }

    props2["tracing"] = lambda_.Tracing.ACTIVE

    return PythonFunction(scope, id, **props2)