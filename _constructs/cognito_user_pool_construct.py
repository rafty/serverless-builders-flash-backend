import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_cognito


class CognitoUserPoolConstruct(Construct):

    def __init__(self,
                 scope: Construct,
                 id: str,
                 user_pool_name: str) -> None:
        super().__init__(scope, id)

        self.__user_pool = aws_cognito.UserPool(
            scope=self,
            id=id,
            user_pool_name=user_pool_name,
            self_sign_up_enabled=True,
            sign_in_aliases={'email': True},
            auto_verify={'email': True},
            removal_policy=cdk.RemovalPolicy.DESTROY,
            password_policy={
                'min_length': 8,
                'require_lowercase': False,
                'require_digits': False,
                'require_uppercase': False,
                'require_symbols': False,
            },
            # account_recovery=aws_cognito.AccountRecovery.EMAIL_ONLY
        )

        # add Domain to User Pool 後でいれるかも
        # aws_cognito.UserPoolDomain(
        #     self,
        #     'UserPoolDomain',
        #     cognito_domain=aws_cognito.CognitoDomainOptions(
        #         domain_prefix='api-user-domain'
        #     ),
        #     user_pool=self.__user_pool
        # )

        # User Pool Client
        self.__user_pool_client = aws_cognito.UserPoolClient(
            self,
            'UserPoolClient',
            user_pool_client_name='JavaScript App',
            user_pool=self.__user_pool,
            generate_secret=False,
            auth_flows={
                # 'admin_user_password': True,
                # 'user_password': True,
                'user_srp': True  # Secure Remote Password
                # 'custom': True,
            },
            prevent_user_existence_errors=True,
            supported_identity_providers=[aws_cognito.UserPoolClientIdentityProvider.COGNITO]
        )

    @property
    def user_pool(self):
        return self.__user_pool

    @property
    def client_id(self):
        return self.__user_pool_client.user_pool_client_id
