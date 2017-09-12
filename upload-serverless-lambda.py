import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
serverless_bucket= s3.Bucket('gwyn-serverless')
serverless_zip_bucket = s3.Bucket('gwyn-serverless-zip')

serverless_zip = StringIO.StringIO()
serverless_zip_bucket.download_fileobj('serverless.zip', serverless_zip)

with zipfile.ZipFile(serverless_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        serverless_bucket.upload_fileobj(obj,nm,ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
        serverless_bucket.Object(nm).Acl().put(ACL='public-read')
