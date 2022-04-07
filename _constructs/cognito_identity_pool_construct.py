from constructs import Construct
from aws_cdk import aws_cognito
from aws_cdk import aws_iam


class CognitoIdentityPoolConstruct(Construct):

    def __init__(self,
                 scope: Construct,
                 id: str,
                 identity_pool_name: str,
                 user_pool,
                 user_pool_client_id) -> None:
        super().__init__(scope, id)

        identity_provider = aws_cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
            client_id=user_pool_client_id,
            provider_name=user_pool.user_pool_provider_name
        )

        self.__identity_pool = aws_cognito.CfnIdentityPool(
            scope=self,
            id=id,
            identity_pool_name=identity_pool_name,
            allow_unauthenticated_identities=True,
            cognito_identity_providers=[identity_provider]
        )

        self.__unauthenticated_role = aws_iam.Role(
            self,
            'UnauthenticatedRole',
            description='Default role for unauthenticated users',
            assumed_by=aws_iam.FederatedPrincipal(
                federated='cognito-identity.amazonaws.com',
                assume_role_action='sts:AssumeRoleWithWebIdentity',
                conditions={
                    'StringEquals': {
                        'cognito-identity.amazonaws.com:aud': self.__identity_pool.ref
                    },
                    'ForAnyValue:StringLike': {
                        'cognito-identity.amazonaws.com:amr': 'unauthenticated'
                    }
                }
            ),
        )

        self.__authenticated_role = aws_iam.Role(
            self,
            'AuthenticatedRole',
            description='Default role for authenticated users',
            assumed_by=aws_iam.FederatedPrincipal(
                federated='cognito-identity.amazonaws.com',
                assume_role_action='sts:AssumeRoleWithWebIdentity',
                conditions={
                    'StringEquals': {
                        'cognito-identity.amazonaws.com:aud': self.__identity_pool.ref
                    },
                    'ForAnyValue:StringLike': {
                        'cognito-identity.amazonaws.com:amr': 'authenticated'
                    }
                }
            ),
        )

        # Attach the two Role
        aws_cognito.CfnIdentityPoolRoleAttachment(
            self,
            'cognito-identity-pool-role-attachment',
            identity_pool_id=self.__identity_pool.ref,
            roles={
                'unauthenticated': self.__unauthenticated_role.role_arn,
                'authenticated': self.__authenticated_role.role_arn
            }
        )

    def unauth_role_allow_invoke(self, apis: list):
        # ----------------------------------------------------------------------------
        # Cognito Id PoolのAuthenticated RoleにAPI Gateway - REST APIのinvoke権限を与える
        # userにexecute-api:invoke権限を与える。なければ403エラーになる。
        # https://aws.amazon.com/jp/premiumsupport/knowledge-center/api-gateway-troubleshoot-403-forbidden/
        # ----------------------------------------------------------------------------
        self.__unauthenticated_role.attach_inline_policy(
            aws_iam.Policy(
                self,
                'APIGatewayGetOnlyPolicy',
                statements=[
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        actions=['execute-api:Invoke'],
                        resources=apis
                    ),
                    # aws_iam.PolicyStatement(
                    #     effect=aws_iam.Effect.ALLOW,
                    #     actions=['execute-api:*'],
                    #     resources=['*']
                    # ),
                ]
            )
        )

    def auth_role_allow_invoke(self, apis: list):
        # ----------------------------------------------------------------------------
        # Cognito Id PoolのAuthenticated RoleにAPI Gateway - REST APIのinvoke権限を与える
        # userにexecute-api:invoke権限を与える。なければ403エラーになる。
        # https://aws.amazon.com/jp/premiumsupport/knowledge-center/api-gateway-troubleshoot-403-forbidden/
        # ----------------------------------------------------------------------------
        self.__authenticated_role.attach_inline_policy(
            aws_iam.Policy(
                self,
                'APIGatewayGetAndPostPolicy',
                statements=[
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        actions=['execute-api:Invoke'],
                        resources=apis
                    ),
                    # aws_iam.PolicyStatement(
                    #     effect=aws_iam.Effect.ALLOW,
                    #     actions=['execute-api:*'],
                    #     resources=['*']
                    # ),
                ]
            )
        )
