# Amazon Forecast Automation
An end to end inventory forecasting demo using AWS Lake Formation for data lake and Amazon Forecast for generating AI driven inventory forecasts.

AWS Glue jobs orchestrated via AWS Glue Workflow to automate the data import, training the predictor and generating forecast export from the Amazon Forecast service.

This is the supporting code for the blog <b> "Building end to end automated inventory forecasting capability with AWS Lake Formation and Amazon Forecast" </b>.

![Solution Architecture](images/InventoryForecast.png)

## Components
1. AWS Glue PySpark job to transform raw data into required format for Amazon Forecast
2. AWS Glue Python shell jobs to load data, train predictor, generate forecast and export forecast to s3 bucket
3. AWS Glue Workflow DAG to orchestrate the above functions

## License

This project is licensed under the Apache-2.0 License.

