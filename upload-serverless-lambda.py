import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes
import os


def lambda_handler(event, context):
    SNS_TOPIC = os.environ.get("SNS_TOPIC")
    ZIPFILE_NAME = os.environ.get("ZIPFILE_NAME")
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    sns = boto3.resource('sns')
    topic = sns.Topic(SNS_TOPIC)
    location = {
        "bucketName": BUCKET_NAME,
        "objectKey": ZIPFILE_NAME
    }
    job = event.get('CodePipeline.job')

    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

    if job:
        for artifact in job['data']['inputArtifacts']:
            if artifact['name'] == 'MyAppBuild':
                location = artifact['location']['s3Location']

    print "Building from " + str(location)

    serverless_bucket= s3.Bucket('gwyn-serverless')
    serverless_zip_bucket = s3.Bucket(location['bucketName'])

    serverless_zip = StringIO.StringIO()
    serverless_zip_bucket.download_fileobj(location['objectKey'], serverless_zip)

    with zipfile.ZipFile(serverless_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            serverless_bucket.upload_fileobj(obj,nm,ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            serverless_bucket.Object(nm).Acl().put(ACL='public-read')
    topic.publish(Subject="Serverless Deploy", Message="Deploy Complete")

    if job:
        codepipeline = boto3.client('codepipeline')
        codepipeline.put_job_success_result(jobId=job['id'])
    return 'Serverless Deploy Complete!'
