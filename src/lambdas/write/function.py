import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')

dynamo = boto3.resource('dynamodb')
table = dynamo.Table('serverless')


def handler(event, context):
    logger.info(f'event={event}')

    item = {
        'Artist': event['artist'],
        'Title': event['title']
    }

    try:
        response = table.put_item(Item=item)
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    else:
        return response
