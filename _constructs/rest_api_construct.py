import aws_cdk
import aws_cdk as cdk
import textwrap
from constructs import Construct
from aws_cdk import aws_apigateway
from aws_cdk import aws_logs
from aws_cdk import aws_iam


class RestApiConstruct(Construct):

    def __init__(self,
                 scope: Construct,
                 id: str,
                 api_name: str,  # api_name: serverless
                 user_pool,
                 write_function,
                 read_function
                 ) -> None:
        super().__init__(scope, id)

        # --------------------------------------------------------
        # Cognito User Poolの作成
        # cognito = CognitoUserPoolConstruct()
        #
        # authorizer 作成
        # 参考
        # https://dev.classmethod.jp/articles/rest-api-authentication-using-cognito/
        # https://github.com/ksmin23/my-aws-cdk-examples/blob/ff3b33108a97706d016e1bdfb29348fb65bb4e98/api-gateway/cognito-api-lambda/app.py
        # --------------------------------------------------------

        # CORSの作成
        _cors_options = aws_apigateway.CorsOptions(
            allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
            allow_methods=aws_apigateway.Cors.ALL_METHODS,
            allow_headers=aws_apigateway.Cors.DEFAULT_HEADERS
        )

        # Access Logの設定
        api_logs = aws_logs.LogGroup(
            self,
            'RestApiLogAccessGroup',
            log_group_name='rest_api/serverless/items',
            retention=aws_logs.RetentionDays.ONE_WEEK,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY
        )

        self.__rest_api = aws_apigateway.RestApi(
            scope=self,
            id=id,
            rest_api_name=api_name,  # serverless
            default_cors_preflight_options=_cors_options,
            # API GatewayのCloudWatch　Logs出力
            # deploy_options=aws_apigateway.StageOptions(
            #     logging_level=aws_apigateway.MethodLoggingLevel.INFO,
            #     metrics_enabled=True,
            #     tracing_enabled=True,
            #     data_trace_enabled=True,  # 実行ログ
            #     access_log_destination=aws_apigateway.LogGroupLogDestination(api_logs),
            #     access_log_format=aws_apigateway.AccessLogFormat.json_with_standard_fields(
            #         caller=True,
            #         http_method=True,
            #         ip=True,
            #         protocol=True,
            #         request_time=True,
            #         resource_path=True,
            #         response_length=True,
            #         status=True,
            #         user=True
            #     )
            # ),
            deploy=False  # stageを指定してDeployするにはFalse
        )

        # ------------------------------------------------------------------
        # add_method('GET')でauthorization_typeがIAMの場合はAuthorizerは必要ない
        # ------------------------------------------------------------------
        # # Authorizer
        # # authorizer = aws_apigateway.CognitoUserPoolsAuthorizer(
        # #     self,
        # #     'AuthorizerForApi',
        # #     cognito_user_pools=[user_pool]
        # # )
        # authorizer = aws_apigateway.CfnAuthorizer(
        #     self,
        #     'ApiGatewayCognitoAuthorizer',
        #     name='serverless_api_cognito_authorizer',
        #     rest_api_id=self.__rest_api.rest_api_id,
        #     type='COGNITO_USER_POOLS',  # aws_apigateway.AuthorizationType.COGNITO
        #     identity_source='method.request.header.Authorization',
        #     provider_arns=[user_pool.user_pool_arn]
        # )

        # Rootのリソース名の作成 (リソースパスと同じ)
        resource_name = 'items'
        items_api = self.__rest_api.root.add_resource(resource_name)

        # -------------------------------
        # Get method
        # -------------------------------
        # API GWのの統合インテグレーション(Lambda版)
        read_lambda_integration = aws_apigateway.LambdaIntegration(
            read_function,
            proxy=False,  # Use proxy integration or normal (request/response mapping) integration. Default: true
            # 通常のAWI GWのIntegration mappingを使わない場合はFalseを指定しなければならない
            # API GWのメソッドリクエスト
            request_templates={
                'application/json': textwrap.dedent(  # json文字列の指定
                    """
                    {
                        "artist": "$input.params('artist')"
                    }
                    """)
            },
            # API GWの統合レスポンス
            integration_responses=[
                aws_apigateway.IntegrationResponse(
                    status_code='200',
                    response_templates={
                        'application/json': ""  # JSONをそのまま返すので空を設定
                    },
                    # CORSなどを指定
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'",  # CORS設定
                    }
                ),
            ]
        )

        self.__items_get = items_api.add_method(
            http_method='GET',
            integration=read_lambda_integration,
            request_parameters={
                # クエリ文字列（URLパラメータ）の明示的に宣言
                'method.request.querystring.artist': True,  # 必須
            },
            method_responses=[
                aws_apigateway.MethodResponse(
                    status_code='200',
                    response_models={
                        'application/json': aws_apigateway.Model.EMPTY_MODEL
                    },
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True  # CORS設定
                    }
                )
            ],
            # authorization_type=aws_apigateway.AuthorizationType.COGNITO
            authorization_type=aws_apigateway.AuthorizationType.IAM
        )
        # authorization_typeがIAMなのでAuthorizerは必要ない。Cognito Tokenなどでは必要
        # self.__items_get.node.find_child('Resource')\
        #     .add_property_override('AuthorizerId', authorizer.ref)

        # -------------------------------
        # POST method
        # -------------------------------
        # API GWのの統合インテグレーション(Lambda版)
        write_lambda_integration = aws_apigateway.LambdaIntegration(
            write_function,
            proxy=False,
            request_templates={
                'application/json': "$input.json('$')"
            },
            integration_responses=[
                aws_apigateway.IntegrationResponse(
                    status_code='200',
                    response_templates={
                        'application/json': ""  # JSONをそのまま返すので空を設定
                    },
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'",  # CORS設定
                    }
                ),
            ]
        )

        self.__items_post = items_api.add_method(
            http_method='POST',
            integration=write_lambda_integration,
            method_responses=[
                aws_apigateway.MethodResponse(
                    status_code='200',
                    response_models={
                        'application/json': aws_apigateway.Model.EMPTY_MODEL
                    },
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True  # CORS設定
                    }
                )
            ],
            # authorization_type=aws_apigateway.AuthorizationType.COGNITO
            authorization_type=aws_apigateway.AuthorizationType.IAM
        )
        # authorization_typeがIAMなのでAuthorizerは必要ない。Cognito Tokenなどでは必要
        # self.__items_post.node.find_child('Resource')\
        #     .add_property_override('AuthorizerId', authorizer.ref)

        # -----------------------------------------------
        # Api の Deployment Stage
        # 各Stageにおいて、API GWがLambdaを呼ぶ権限を与える
        # -----------------------------------------------
        api_deployment = aws_apigateway.Deployment(
            self,
            'ItemsApiDeployment',
            api=self.__rest_api,
            retain_deployments=False
        )
        # dev_stage = aws_apigateway.Stage(
        #     self,
        #     'DevStage',
        #     stage_name='dev',
        #     deployment=api_deployment
        # )

        stg_stage = aws_apigateway.Stage(
            self,
            'StgStage',
            stage_name='stg',
            deployment=api_deployment
        )

        prod_stage = aws_apigateway.Stage(
            self,
            'ProdStage',
            stage_name='prod',
            deployment=api_deployment
        )

        self.__rest_api.deployment_stage = stg_stage

        # デプロイメントを自分で指定する際、API GWがLambdaを呼び出す権限を自分で設定する
        read_function.add_permission(
            'ReadLambdaPermission',
            action='lambda:InvokeFunction',
            principal=aws_iam.ServicePrincipal('apigateway.amazonaws.com'),
            source_arn=self.__items_get.method_arn.replace(
                self.__rest_api.deployment_stage.stage_name, '*'
            )
        )
        # デプロイメントを自分で指定する際、API GWがLambdaを呼び出す権限を自分で設定する
        write_function.add_permission(
            'WriteLambdaPermission',
            action='lambda:InvokeFunction',
            principal=aws_iam.ServicePrincipal('apigateway.amazonaws.com'),
            source_arn=self.__items_post.method_arn.replace(
                self.__rest_api.deployment_stage.stage_name, '*'
            )
        )

    @property
    def items_get_api(self):
        return self.__items_get

    @property
    def items_post_api(self):
        return self.__items_post
