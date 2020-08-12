import sys
import boto3

session = boto3.Session()
forecast = session.client(service_name='forecast') 
glue_client = session.client(service_name='glue')

forecastHorizon = 90
workflowName = 'AmazonForecastWorkflow'
workflow = glue_client.get_workflow(Name=workflowName)
workflow_params = workflow['Workflow']['LastRun']['WorkflowRunProperties']
workflowRunId = workflow['Workflow']['LastRun']['WorkflowRunId']
datasetGroupArn = workflow_params['datasetGroupArn']
project = workflow_params['projectName']
predictorName= project + '_ETS'

create_predictor_response=forecast.create_predictor(PredictorName=predictorName,
                                                AlgorithmArn='arn:aws:forecast:::algorithm/ETS',
                                                ForecastHorizon=forecastHorizon,
                                                PerformAutoML= False,
                                                PerformHPO=False,
                                                EvaluationParameters= {"NumberOfBacktestWindows": 1, 
                                                                        "BackTestWindowOffset": 90}, 
                                                InputDataConfig= {"DatasetGroupArn": datasetGroupArn},
                                                FeaturizationConfig= {"ForecastFrequency": "D", 
                                                                       'ForecastDimensions': [
                                                                            'location'
                                                                        ],
                                                                    "Featurizations": 
                                                                    [
                                                                        {"AttributeName": "demand", 
                                                                        "FeaturizationPipeline": 
                                                                        [
                                                                            {"FeaturizationMethodName": "filling", 
                                                                            "FeaturizationMethodParameters": 
                                                                            {"frontfill": "none", 
                                                                                "middlefill": "zero", 
                                                                                "backfill": "zero"}
                                                                            }
                                                                        ]
                                                                        }
                                                                    ]
                                                                    }
                                                    )
predictorArn=create_predictor_response['PredictorArn']

workflow_params['predictorArn'] = predictorArn
glue_client.put_workflow_run_properties(Name=workflowName, RunId=workflowRunId, RunProperties=workflow_params)
workflow_params = glue_client.get_workflow_run_properties(Name=workflowName,
                                        RunId=workflowRunId)["RunProperties"]

print('output Predictor Arn is: ' + workflow_params['predictorArn'])
