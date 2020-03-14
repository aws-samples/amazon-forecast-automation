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
orders_import_job_arn = workflow_params['ordersImportJobRunId']
products_import_job_arn = workflow_params['productsImportJobRunId']
# initialise import job status for while loop
ordersDataImportStatus = forecast.describe_dataset_import_job(DatasetImportJobArn=orders_import_job_arn)['Status']
productsDataImportStatus = forecast.describe_dataset_import_job(DatasetImportJobArn=products_import_job_arn)['Status']

while (ordersDataImportStatus != 'ACTIVE' and productsDataImportStatus != 'ACTIVE'):
    ordersDataImportStatus = forecast.describe_dataset_import_job(DatasetImportJobArn=orders_import_job_arn)['Status']
    productsDataImportStatus = forecast.describe_dataset_import_job(DatasetImportJobArn=products_import_job_arn)['Status']
    if (ordersDataImportStatus == 'CREATE_FAILED' or productsDataImportStatus == 'CREATE_FAILED'):
        raise NameError('Import create failed')
    time.sleep(20)

print ('Orders Import status is: ' + ordersDataImportStatus)
print ('Products Import status is: ' + productsDataImportStatus)
