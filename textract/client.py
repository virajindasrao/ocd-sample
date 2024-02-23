import boto3, os

def client():
    return boto3.Session(
        region_name='eu-west-1').client(
            'textract', 
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
            aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))
    