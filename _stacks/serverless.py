from aws_cdk import Stack
from constructs import Construct
from _constructs.dynamo_construct import DynamoDbTableConstruct
from _constructs.lambda_construct import LambdaFunctionConstruct
from _constructs.rest_api_construct import RestApiConstruct
from _constructs.cognito_user_pool_construct import CognitoUserPoolConstruct
from _constructs.cognito_identity_pool_construct import CognitoIdentityPoolConstruct


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

        # Cognito User Pool
        cognito_user_pool = CognitoUserPoolConstruct(
            self,
            'CognitoUserPoolForApiGateway',
            user_pool_name='UserPoolForApiGateway'
        )

        # API Gateway & Lambda Integration
        rest_api = RestApiConstruct(
            self,
            'ServerlessApiRead',
            api_name='serverless',
            user_pool=cognito_user_pool.user_pool,
            write_function=write_lambda.function,
            read_function=read_lambda.function
        )

        # Cognito Identity Pool
        cognito_identity_pool = CognitoIdentityPoolConstruct(
            self,
            'CognitoIdentityPoolForApiGateway',
            identity_pool_name='IdentityPoolForApiGateway',
            user_pool=cognito_user_pool.user_pool,
            user_pool_client_id=cognito_user_pool.client_id
        )


        cognito_identity_pool.auth_role_allow_invoke(
            [
                rest_api.items_get_api.method_arn,
                rest_api.items_post_api.method_arn
            ]
        )

        cognito_identity_pool.unauth_role_allow_invoke(
            [
                rest_api.items_get_api.method_arn
            ]
        )
