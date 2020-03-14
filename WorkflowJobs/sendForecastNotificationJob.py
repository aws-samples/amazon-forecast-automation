import sys
import boto3
import datetime
from awsglue.utils import getResolvedOptions

session = boto3.Session(region_name='us-west-2') 
sns = session.client(service_name='sns')
glue_client = session.client(service_name='glue')

workflowName = 'AmazonForecastWorkflow'
workflow = glue_client.get_workflow(Name=workflowName)
workflow_params = workflow['Workflow']['LastRun']['WorkflowRunProperties']
workflowRunId = workflow['Workflow']['LastRun']['WorkflowRunId']
forecastName = workflow_params['forecastName']
dt = datetime.datetime.now()
payload = 'The latest forecast report ' + forecastName + ' is ready. Click https://us-west-2.quicksight.aws.amazon.com/sn/dashboards/3d72dce2-197e-4e88-a02a-6f043c56d8ac to view.'

topics = sns.list_topics()
topicArn = topics['Topics'][0]['TopicArn']

response = sns.publish(
    TopicArn=topicArn,
    Message=payload,
    Subject='Inventory Planning Forecast'
)

print('Publish response: ' + response['MessageId'])
