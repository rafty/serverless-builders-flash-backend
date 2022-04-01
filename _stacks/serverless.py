from aws_cdk import Stack
from constructs import Construct
from _constructs.dynamo_construct import DynamoDbTableConstruct
from _constructs.lambda_construct import LambdaFunctionConstruct


class ServerlessStack(Stack):

    def __init__(self,
                 scope: Construct,
                 construct_id: str,
                 **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        write_lambda = LambdaFunctionConstruct(
            self,
            'FunctionWrite',
            src='src/lambdas/write',
            function_name='backend_write'
        )

        read_lambda = LambdaFunctionConstruct(
            self,
            'FunctionRead',
            src='src/lambdas/read',
            function_name='backend_read'
        )

        dynamodb = DynamoDbTableConstruct(
            self,
            'ServerlessDB',
            name='serverless',
            partition='Artist',
            sort='Title'
        )
        dynamodb.table.grant_read_write_data(write_lambda.function)
        dynamodb.table.grant_read_write_data(read_lambda.function)
