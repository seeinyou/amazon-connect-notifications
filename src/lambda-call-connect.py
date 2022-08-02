import json
import boto3
import logging
import os
import botocore.session
from botocore.exceptions import ClientError

session = botocore.session.get_session()
logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)

# Lambda handler
def lambda_handler(event, context):
    # Debug
    logger.setLevel(logging.DEBUG)
    print(event)
    
    DestPhoneNumber = os.environ['DestPhoneNumber']          #Getting the destination phone number passed in by the environment variables.
    ContactFlowId = os.environ['ContactFlowId']              #Getting the Amazon Connect ContactFlowID passed in by the environment variables.
    InstanceId = os.environ['InstanceId']                    #Getting the Amazon Connect InstanceId passed in by the environment variables.
    SourcePhoneNumber = os.environ['SourcePhoneNumber']      #Getting the Source Phone Number passed in by the environment variables. This phone number is your Amazon Connect phone number.

    # Load all parameters
    eventname = event['detail']['Message']
    eventCategories = event['detail']['EventCategories'][0]
    eventRegion = event['region']
    eventSource = event['detail']['SourceIdentifier']
    
    # Debug
    logger.debug("Event is --- %s" %event)
    logger.debug("Event Name is--- %s" %eventname)
    logger.debug("DestPhoneNumber is-- %s" %DestPhoneNumber)

    # Initialize the boto3 client object
    client = boto3.client('iam')
    connectclient = boto3.client('connect')
    response = client.list_account_aliases()
    
    # Debug
    logger.debug("List account alias response --- %s" %response)
    
    try:
        if not response['AccountAliases']:
            accntAliase = (boto3.client('sts').get_caller_identity()['Account'])
            logger.info("Account alias is not defined. Account ID is %s" %accntAliase)
        else:
            accntAliase = response['AccountAliases'][0]
            logger.info("Account alias is : %s" %accntAliase)
    
    except ClientError as e:
        logger.error("Client error occurred")
    
    try: 
        #Making the outbound phone alert...
        OutboundResponse = connectclient.start_outbound_voice_contact(
                      DestinationPhoneNumber=DestPhoneNumber,
                      ContactFlowId=ContactFlowId,
                      InstanceId=InstanceId,
                      SourcePhoneNumber=SourcePhoneNumber,
                      Attributes={'Message': 'This is a critical alert message! Amazon RDS %s event-%s on resource-%s detected in account-%s' %(eventCategories, eventname, eventSource, accntAliase)
                                  }
                      )
    
        logger.debug("outbound Call response is-- %s" %OutboundResponse)
    except ClientError as e:
        logger.error("An error occurred: %s" %e)

    return OutboundResponse