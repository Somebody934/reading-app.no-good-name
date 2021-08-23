import boto3
import os

# FILE STORAGE

session = boto3.Session()
s3_client = boto3.client('s3',
                         aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                         aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                         )
s3 = boto3.resource('s3')
bucket_name = os.getenv("S3_BUCKET_NAME")
s3_path = os.getenv("LOCAL_S3_PATH", "local")
bucket = s3.Bucket(bucket_name)


def read_file(user_id, path):
    """
    user_id - User
    path - only for current user
    """
    full_path = s3_path + f"/users/{user_id}/" + path
    list_of_files = bucket.objects.filter(Prefix=full_path)
    story_dict = {}
    for obj in list_of_files:
        key = obj.key
        body = obj.get()['Body'].read()
        last_part = key.split("/")[-1]
        story_dict[last_part] = body
    return story_dict


def upload_file(user_id, path, text):
    full_path = s3_path + f"/users/{user_id}/" + path
    s3_client.put_object(Body=text, Bucket=bucket_name, Key=full_path)

def delete_file(user_id, path):
    full_path = s3_path + f"/users/{user_id}/" + path
    s3.Object(bucket_name=bucket_name, key=full_path).delete()