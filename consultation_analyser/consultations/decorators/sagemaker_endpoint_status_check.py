import boto3
from django.conf import settings


def check_and_launch_sagemaker(func):
    def wrapper(request, *args, **kwargs):
        sagemaker = boto3.client("sagemaker")
        endpoint_name = settings.SAGEMAKER_ENDPOINT_NAME
        if not endpoint_name:
            return func(request, *args, **kwargs)
        try:
            sagemaker.describe_endpoint(EndpointName=endpoint_name)
            print(f"Endpoint {endpoint_name} already exists. Skipping creation.")

        except boto3.exceptions.botocore.exceptions.ClientError as _:
            sagemaker.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_name,
            )
            print(f"Endpoint {endpoint_name} has been created.")
        return func(request, *args, **kwargs)

    return wrapper
