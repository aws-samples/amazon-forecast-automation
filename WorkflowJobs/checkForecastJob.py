import sys
import boto3
import time

session = boto3.Session()
forecast = session.client(service_name='forecast') 
glue_client = session.client(service_name='glue')

workflowName = 'AmazonForecastWorkflow'
workflow = glue_client.get_workflow(Name=workflowName)
workflow_params = workflow['Workflow']['LastRun']['WorkflowRunProperties']
workflowRunId = workflow['Workflow']['LastRun']['WorkflowRunId']
forecastArn = workflow_params['forecastArn']
# initialise forecast job status for while loop
forecastStatus = forecast.describe_forecast(ForecastArn=forecastArn)['Status']

while (forecastStatus != 'ACTIVE'):
    forecastStatus = forecast.describe_forecast(ForecastArn=forecastArn)['Status']
    if (forecastStatus == 'CREATE_FAILED'):
        raise NameError('Forecast create failed')
    time.sleep(20)

print ('Forecast status is: ' + forecastStatus)
