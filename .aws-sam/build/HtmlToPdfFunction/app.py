from datetime import datetime
import json
import logging
import os
import subprocess
from typing import Optional
import boto3
from botocore.exceptions import ClientError


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get the s3 client
s3 = boto3.client('s3')

def download_s3_file(bucket: str, file_key: str) -> str:
    """Downloads a file from s3 to `/tmp/[File Key]`.
    
    Args:
        bucket (str): Name of the bucket where the file lives.
        file_key (str): The file key of the file in the bucket.
    Returns:
    	The local file name as a string.
    """
    local_filename = f'/tmp/{file_key}'
    s3.download_file(Bucket=bucket, Key=file_key, Filename=local_filename)
    logger.info('Downloaded HTML file to %s' % local_filename)

    return local_filename
    
    
def upload_file_to_s3(bucket: str, filename: str) -> Optional[str]:
    """Uploads the generated PDF to s3.
    
    Args:
        bucket (str): Name of the s3 bucket to upload the PDF to.
        filename (str): Location of the file to upload to s3.
        
    Returns:
        The file key of the file in s3 if the upload was successful.
        If the upload failed, then `None` will be returned.
    """
    file_key = None
    try:
        file_key = filename.replace('/tmp/', '')
        s3.upload_file(Filename=filename, Bucket=bucket, Key=file_key)
        logger.info('Successfully uploaded the PDF to %s as %s'
                    % (bucket, file_key))
    except ClientError as e:
        logger.error('Failed to upload file to s3.')
        logger.error(e)
        file_key = None
        
    return file_key

def lambda_handler(event, context):
    logger.info(event)

    # bucket is always required
    try:
        bucket = event['bucket']
    except KeyError:
        error_message = 'Missing required "bucket" parameter from request payload.'
        logger.error(error_message)
        return {
            'status': 400,
            'body': json.dumps(error_message),
        }

    # html_string and file_key are conditionally required, so let's try to get both
    try:
        file_key = event['file_key']
    except KeyError:
        file_key = None

    try:
        html_string = event['html_string']
    except KeyError:
        html_string = None

    if file_key is None and html_string is None:
        error_message = (
            'Missing both a "file_key" and "html_string" '
            'from request payload. One of these must be '
            'included.'
        )
        logger.error(error_message)
        return {
            'status': 400,
            'body': json.dumps(error_message),
        }

    # Now we can check for the option wkhtmltopdf_options and map them to values
    # Again, part of our assumptions are that these are valid
    wkhtmltopdf_options = {}
    if 'wkhtmltopdf_options' in event:
        # Margin is <top> <right> <bottom> <left>
        if 'margin' in event['wkhtmltopdf_options']:
            margins = event['wkhtmltopdf_options']['margin'].split(' ')
            if len(margins) == 4:
                wkhtmltopdf_options['margin-top'] = margins[0]
                wkhtmltopdf_options['margin-right'] = margins[1]
                wkhtmltopdf_options['margin-bottom'] = margins[2]
                wkhtmltopdf_options['margin-left'] = margins[3]

        if 'orientation' in event['wkhtmltopdf_options']:
            wkhtmltopdf_options['orientation'] = 'portrait' \
                if event['wkhtmltopdf_options']['orientation'].lower() not in ['portrait', 'landscape'] \
                else event['wkhtmltopdf_options']['orientation'].lower()

        if 'title' in event['wkhtmltopdf_options']:
            wkhtmltopdf_options['title'] = event['wkhtmltopdf_options']['title']

    # If we got a file_key in the request, let's download our file
    # If not, we'll write the HTML string to a file
    if file_key is not None:
        local_filename = download_s3_file(bucket, file_key)
    else:
        timestamp = str(datetime.now()).replace('.', '').replace(' ', '_')
        local_filename = f'/tmp/{timestamp}-html-string.html'

        # Delete any existing files with that name
        try:
            os.unlink(local_filename)
        except FileNotFoundError:
            pass

        with open(local_filename, 'w') as f:
            f.write(html_string)

    # Now we can create our command string to execute and upload the result to s3
    command = 'wkhtmltopdf  --load-error-handling ignore'  # ignore unecessary errors
    for key, value in wkhtmltopdf_options.items():
        if key == 'title':
            value = f'"{value}"'
        command += ' --{0} {1}'.format(key, value)
    command += ' {0} {1}'.format(local_filename, local_filename.replace('.html', '.pdf'))

    # Important! Remember, we said that we are assuming we're accepting valid HTML
    # this should always be checked to avoid allowing any string to be executed
    # from this command. The reason we use shell=True here is because our title
    # can be multiple words.
    subprocess.run(command, shell=True)
    logger.info('Successfully generated the PDF.')
    file_key = upload_file_to_s3(bucket, local_filename.replace('.html', '.pdf'))

    if file_key is None:
        error_message = (
            'Failed to generate PDF from the given HTML file.'
            ' Please check to make sure the file is valid HTML.'
        )
        logger.error(error_message)
        return {
            'status': 400,
            'body': json.dumps(error_message),
        }

    return {
        'status': 200,
        'file_key': file_key,
    }
