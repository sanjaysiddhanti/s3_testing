from unittest.mock import patch

import boto3
import pytest

from recipe import Recipe, S3_BUCKET


@pytest.fixture
def s3_localstack():
    s3 = boto3.client("s3", endpoint_url="http://localstack:4572")
    s3.create_bucket(Bucket=S3_BUCKET)
    with patch("recipe.get_s3", return_value=s3):
        yield s3


def test_create_and_get(s3_localstack):
    Recipe(name="nachos", instructions="Melt cheese on chips").save()

    recipe = Recipe.get_by_name("nachos")
    assert recipe.name == "nachos"
    assert recipe.instructions == "Melt cheese on chips"


def test_get_does_not_exist(s3_localstack):
    with pytest.raises(s3_localstack.exceptions.NoSuchKey):
        recipe = Recipe.get_by_name("sandwich")


def test_update(s3_localstack):
    old_instructions = "Melt cheese on chips"
    new_instructions = "Microwave a plate full of tortilla chips and cheese"

    Recipe(name="nachos", instructions=old_instructions).save()

    new_recipe = Recipe.update_instructions(
        name="nachos", new_instructions=new_instructions
    )

    # Nothing changes until you call save()
    recipe = Recipe.get_by_name("nachos")
    assert recipe.instructions == old_instructions

    new_recipe.save()

    # Recipe updates after saving
    recipe = Recipe.get_by_name("nachos")
    assert recipe.instructions == new_instructions


def test_delete(s3_localstack):
    Recipe(name="nachos", instructions="Melt cheese on chips").save()

    response = s3_localstack.list_objects_v2(Bucket=S3_BUCKET)
    assert len(response["Contents"]) == 1
    assert response["Contents"][0]["Key"] == "nachos"

    Recipe.delete("nachos")

    # Data in S3 is gone after deleting the recipe
    response = s3_localstack.list_objects_v2(Bucket=S3_BUCKET)
    assert "Contents" not in response.keys()
