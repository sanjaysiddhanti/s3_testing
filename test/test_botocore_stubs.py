import datetime
import json
from dateutil.tz import tzutc
from io import BytesIO
from unittest.mock import patch

import boto3
from botocore.stub import Stubber, ANY
from botocore.response import StreamingBody
from moto import mock_s3
import pytest

from recipe import Recipe, S3_BUCKET


@pytest.fixture
def s3_stub():
    """Pytest fixture that mocks the get_s3 function with a S3 client stub
    
    Yields a Stubber for the S3 client
    """
    s3 = boto3.client("s3")
    stubber = Stubber(s3)

    with patch("recipe.get_s3", return_value=s3):
        yield stubber


def test_create_and_get(s3_stub):
    # Stub out the put_object response
    # Note: These stubs are incomplete - I omitted things such as HTTP headers for brevity
    put_object_response = {
        "ResponseMetadata": {
            "RequestId": "5994D680BF127CE3",
            "HTTPStatusCode": 200,
            "RetryAttempts": 1,
        },
        "ETag": '"6299528715bad0e3510d1e4c4952ee7e"',
    }
    put_object_expected_params = {"Bucket": ANY, "Key": ANY, "Body": ANY}
    s3_stub.add_response("put_object", put_object_response, put_object_expected_params)

    # Create the StreamingBody that will be returned by get_object
    encoded_message = json.dumps(
        {"name": "nachos", "instructions": "Melt cheese on chips"}
    ).encode("utf-8")
    raw_stream = StreamingBody(BytesIO(encoded_message), len(encoded_message))

    # Stub out the get_object response
    get_object_response = {
        "ResponseMetadata": {
            "RequestId": "6BFC00970E62BC8F",
            "HTTPStatusCode": 200,
            "RetryAttempts": 1,
        },
        "LastModified": datetime.datetime(2020, 4, 6, 5, 39, 29, tzinfo=tzutc()),
        "ContentLength": 58,
        "ETag": '"6299528715bad0e3510d1e4c4952ee7e"',
        "ContentType": "binary/octet-stream",
        "Metadata": {},
        "Body": raw_stream,
    }
    get_object_expected_params = {"Bucket": ANY, "Key": ANY}
    s3_stub.add_response("get_object", get_object_response, get_object_expected_params)

    # Activate the stubber
    with s3_stub:
        recipe = Recipe.new(name="nachos", instructions="Melt cheese on chips")
        recipe.save()

        recipe = Recipe.get_by_name("nachos")
        assert recipe.name == "nachos"
        assert recipe.instructions == "Melt cheese on chips"
