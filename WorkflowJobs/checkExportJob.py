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
forecastExportArn = workflow_params['forecastExportArn']
# initialise forecast job status for while loop
forecastExportStatus = forecast.describe_forecast_export_job(ForecastExportJobArn=forecastExportArn)['Status']

while (forecastExportStatus != 'ACTIVE'):
    forecastExportStatus = forecast.describe_forecast_export_job(ForecastExportJobArn=forecastExportArn)['Status']
    if (forecastExportStatus == 'CREATE_FAILED'):
        raise NameError('Forecast export failed')
    time.sleep(20)

print ('Forecast export status is: ' + forecastExportStatus)
