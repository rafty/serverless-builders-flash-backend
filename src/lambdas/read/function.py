import logging
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamo = boto3.resource('dynamodb')
table = dynamo.Table('serverless')

logger.info('Loading function')


def handler(event, context):
    logger.info(f'event={event}')

    try:
        response = table.query(
            KeyConditionExpression=Key('Artist').eq(event['artist'])
        )
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    else:
        return response['Items']
