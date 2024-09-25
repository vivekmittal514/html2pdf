# html2pdf

This project simplifies the process of converting HTML files to PDF using the serverless framework. It leverages AWS Lambda and AWS Serverless Application Model (SAM) to build and deploy the solution.

The project includes the following key components:

1. **HTML to PDF Lambda Function**: The source code for the Lambda function that performs the HTML to PDF conversion is located in the `html_to_pdf` directory.
2. **AWS SAM Template**: The `template.yaml` file defines the AWS resources required for the application, including the Lambda function and its associated components.

The application utilizes a lambda layer provided by the [wkhtmltopdf project](https://wkhtmltopdf.org/) to handle the HTML to PDF conversion. This allows the solution to benefit from the robust functionality and performance of the wkhtmltopdf library without the need to manage the dependencies within the Lambda function code.

To test the application, you can provide an input event in the following JSON format:

```json
{
    "bucket": "<Name of the bucket where the file is stored currently and will be stored after processing> [Required]",
    "file_key": "<File key where the file is store in S3> [Required if `html_string` is not defined]",
    "html_string": "<HTML string to convert to a PDF> [Required if `file_key` is not defined]",
    "wkhtmltopdf_options": {
        "orientation": "<`landscape` or `portrait`> [Optional: Default is `portrait`]",
        "title": "<Title of the PDF> [Optional]",
        "margin": "<Margin of the PDF (same format as css [<top> <right> <bottom> <left>] (all must be included)).> [Optional]"
    }
}
```

When the Lambda function is executed, it will retrieve the HTML file from an S3 bucket, convert it to a PDF, and store the resulting PDF file in the same S3 bucket.

This serverless approach simplifies the deployment and management of the HTML to PDF conversion functionality, making it easier to integrate and scale as needed.


## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
sam delete --stack-name "html2pdf"
```