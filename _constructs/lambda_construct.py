import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_lambda


class LambdaFunctionConstruct(Construct):

    def __init__(self,
                 scope: Construct,
                 id: str,
                 src: str,
                 function_name: str) -> None:

        super().__init__(scope, id)

        self.__function = aws_lambda.Function(
            scope=self,
            id=id,
            function_name=function_name,
            handler='function.handler',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(src),
            timeout=cdk.Duration.seconds(amount=60)
        )

    @property
    def function(self):
        return self.__function
