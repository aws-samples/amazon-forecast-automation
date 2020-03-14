import sys
import boto3
import time
from awsglue.utils import getResolvedOptions

session = boto3.Session(region_name='us-west-2') 
forecast = session.client(service_name='forecast') 
glue_client = session.client(service_name='glue')

workflowName = 'AmazonForecastWorkflow'
workflow = glue_client.get_workflow(Name=workflowName)
workflow_params = workflow['Workflow']['LastRun']['WorkflowRunProperties']
workflowRunId = workflow['Workflow']['LastRun']['WorkflowRunId']
predictorArn = workflow_params['predictorArn']
# initialise predictor job status for while loop
predictorStatus = forecast.describe_predictor(PredictorArn=predictorArn)['Status']

while (predictorStatus != 'ACTIVE'):
    predictorStatus = forecast.describe_predictor(PredictorArn=predictorArn)['Status']
    if (predictorStatus == 'CREATE_FAILED'):
        raise NameError('Predictor create failed')
    time.sleep(20)

print ('Predictor status is: ' + predictorStatus)
