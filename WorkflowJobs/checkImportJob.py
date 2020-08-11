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
orders_import_ds_arn = workflow_params['targetTimeSeriesDataset']
products_import_ds_arn = workflow_params['itemMetaDataset']
# initialise import job status for while loop
ordersDataImportStatus = forecast.describe_dataset(DatasetArn=orders_import_ds_arn)['Status']
productsDataImportStatus = forecast.describe_dataset(DatasetArn=products_import_ds_arn)['Status']

while True:    
    if (ordersDataImportStatus == 'ACTIVE' and productsDataImportStatus == 'ACTIVE'):
        break
    elif (ordersDataImportStatus == 'CREATE_FAILED' or productsDataImportStatus == 'CREATE_FAILED'):
        raise NameError('Import create failed')
    ordersDataImportStatus = forecast.describe_dataset(DatasetArn=orders_import_ds_arn)['Status']
    productsDataImportStatus = forecast.describe_dataset(DatasetArn=products_import_ds_arn)['Status']       
    time.sleep(20)

print ('Orders Import status is: ' + ordersDataImportStatus)
print ('Products Import status is: ' + productsDataImportStatus)
