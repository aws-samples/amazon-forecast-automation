import sys
import boto3
import datetime
import random

session = boto3.Session()
forecast = session.client(service_name='forecast') 
glue_client = session.client(service_name='glue')

workflowName = 'AmazonForecastWorkflow'
workflow = glue_client.get_workflow(Name=workflowName)
workflow_params = workflow['Workflow']['LastRun']['WorkflowRunProperties']
workflowRunId = workflow['Workflow']['LastRun']['WorkflowRunId']
iam = session.resource('iam')

# In our dataset, the timeseries values are recorded every day
DATASET_FREQUENCY = "D" 
TIMESTAMP_FORMAT = "yyyy-MM-dd hh:mm:ss"

rnd = str(random.getrandbits(12))
project = 'inventory_forecast_' + rnd
datasetName = project + '_ds'
datasetGroupName = project + '_dsg'
bucket_name = workflow_params['processedBucket']
orders_file = 'orders/orders-data.csv'
products_file = 'products/product-data.csv'
role = iam.Role('GLUE_WORKFLOW_ROLE')
s3DataPathOrders = 's3://' + bucket_name + '/' + orders_file
s3DataPathProducts = 's3://' + bucket_name + '/' + products_file

create_dataset_group_response = forecast.create_dataset_group(DatasetGroupName=datasetGroupName,
                                                            Domain="INVENTORY_PLANNING",
                                                            )
datasetGroupArn = create_dataset_group_response['DatasetGroupArn']
workflow_params['datasetGroupArn'] = datasetGroupArn
workflow_params['projectName'] = project

def start_orders_import_job(s3DataPath, datasetName, datasetGroupArn, role_arn):
    # Specify the schema of your dataset here. Make sure the order of columns matches the raw data files.
    schema = {
    "Attributes": [
        {
            "AttributeName": "timestamp",
            "AttributeType": "timestamp"
        },
        {
            "AttributeName": "item_id",
            "AttributeType": "string"
        },
        {
            "AttributeName": "demand",
            "AttributeType": "integer"
        },
        {
            "AttributeName": "location",
            "AttributeType": "string"
        }
    ]
    }

    response = forecast.create_dataset(
                    Domain="INVENTORY_PLANNING",
                    DatasetType='TARGET_TIME_SERIES',
                    DatasetName=datasetName,
                    DataFrequency=DATASET_FREQUENCY, 
                    Schema = schema)

    TargetdatasetArn = response['DatasetArn']
    workflow_params['targetTimeSeriesDataset'] = TargetdatasetArn
    updateDatasetResponse = forecast.update_dataset_group(DatasetGroupArn=datasetGroupArn, DatasetArns=[TargetdatasetArn])

    # Orders dataset import job
    datasetImportJobName = 'INVENTORY_DSIMPORT_JOB_TARGET'
    ds_import_job_response=forecast.create_dataset_import_job(DatasetImportJobName=datasetImportJobName,
                                                            DatasetArn=TargetdatasetArn,
                                                            DataSource= {
                                                                "S3Config" : {
                                                                    "Path": s3DataPathOrders,
                                                                    "RoleArn": role_arn
                                                                } 
                                                            },
                                                            TimestampFormat=TIMESTAMP_FORMAT
                                                            )

    ds_import_job_arn=ds_import_job_response['DatasetImportJobArn']

    workflow_params['ordersImportJobRunId'] = ds_import_job_arn
    
    return {
    "importJobArn": ds_import_job_arn,
    "datasetGroupArn": datasetGroupArn,
    "ordersDatasetArn": TargetdatasetArn
    }

def start_products_import_job(s3DataPath, datasetName, datasetGroupArn, role_arn, ordersDatasetArn):
        # Specify the schema of your dataset here. Make sure the order of columns matches the raw data files.
    schema = {
        "Attributes": [
            {
                "AttributeName": "item_id",
                "AttributeType": "string"
            },
            {
                "AttributeName": "description",
                "AttributeType": "string"
            },
            {
                "AttributeName": "price",
                "AttributeType": "float"
            }
        ]
    }

    response = forecast.create_dataset(
                    Domain="INVENTORY_PLANNING",
                    DatasetType='ITEM_METADATA',
                    DatasetName=datasetName+'_2',
                    DataFrequency=DATASET_FREQUENCY, 
                    Schema = schema)

    metaDatasetArn = response['DatasetArn']
    workflow_params['itemMetaDataset'] = metaDatasetArn
    updateDatasetResponse = forecast.update_dataset_group(DatasetGroupArn=datasetGroupArn, DatasetArns=[ordersDatasetArn, metaDatasetArn])

    # Dataset import job
    datasetImportJobName = 'INVENTORY_DSIMPORT_JOB_METADATA'
    ds_import_job_response=forecast.create_dataset_import_job(DatasetImportJobName=datasetImportJobName,
                                                          DatasetArn=metaDatasetArn,
                                                          DataSource= {
                                                              "S3Config" : {
                                                                 "Path": s3DataPathProducts,
                                                                 "RoleArn": role_arn
                                                              } 
                                                          },
                                                          TimestampFormat=TIMESTAMP_FORMAT
                                                         )

    ds_import_job_arn=ds_import_job_response['DatasetImportJobArn']

    workflow_params['productsImportJobRunId'] = ds_import_job_arn
    return

orders_import_result = start_orders_import_job(s3DataPathOrders, datasetName, datasetGroupArn, role.arn)
products_import_result = start_products_import_job(s3DataPathProducts, datasetName, datasetGroupArn, role.arn, orders_import_result['ordersDatasetArn'])

glue_client.put_workflow_run_properties(Name=workflowName, RunId=workflowRunId, RunProperties=workflow_params)
workflow_params = glue_client.get_workflow_run_properties(Name=workflowName,
                                        RunId=workflowRunId)["RunProperties"]

print('output OrdersImportJObId is: ' + workflow_params['ordersImportJobRunId'])
print('output ProductsImportJObId is: ' + workflow_params['productsImportJobRunId'])
print('output Dataset Group Arn is: ' + workflow_params['datasetGroupArn'])
print('output Item Dataset Arn is: ' + workflow_params['targetTimeSeriesDataset'])
print('output Meta Dataset Arn is: ' + workflow_params['itemMetaDataset'])