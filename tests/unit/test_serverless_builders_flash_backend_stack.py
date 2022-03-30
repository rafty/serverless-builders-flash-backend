import aws_cdk as core
import aws_cdk.assertions as assertions

from serverless_builders_flash_backend.serverless_builders_flash_backend_stack import ServerlessBuildersFlashBackendStack

# example tests. To run these tests, uncomment this file along with the example
# resource in serverless_builders_flash_backend/serverless_builders_flash_backend_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ServerlessBuildersFlashBackendStack(app, "serverless-builders-flash-backend")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
