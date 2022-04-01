import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_dynamodb


class DynamoDbTableConstruct(Construct):

    def __init__(self,
                 scope: Construct,
                 id: str,
                 name: str,
                 partition: str,
                 sort: str) -> None:

        super().__init__(scope, id)

        self.__table = aws_dynamodb.Table(
            self,
            id=id,
            table_name=name,
            partition_key=aws_dynamodb.Attribute(name=partition, type=aws_dynamodb.AttributeType.STRING),
            sort_key=aws_dynamodb.Attribute(name=sort, type=aws_dynamodb.AttributeType.STRING)
        )

    @property
    def table(self):
        return self.__table
