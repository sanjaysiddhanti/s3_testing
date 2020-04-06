import boto3
from moto import mock_s3
import pytest


from recipe import Recipe, S3_BUCKET


@pytest.fixture
def s3():
    """Pytest fixture that creates the recipes bucket in 
    the fake moto AWS account
    
    Yields a fake boto3 s3 client
    """
    with mock_s3():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=S3_BUCKET)
        yield s3


def test_create_and_get(s3):
    Recipe.new(name="nachos", instructions="Melt cheese on chips").save()

    recipe = Recipe.get_by_name("nachos")
    assert recipe.name == "nachos"
    assert recipe.instructions == "Melt cheese on chips"


def test_get_does_not_exist(s3):
    with pytest.raises(s3.exceptions.NoSuchKey):
        recipe = Recipe.get_by_name("sandwich")


def test_update(s3):
    old_instructions = "Melt cheese on chips"
    new_instructions = "Microwave a plate full of tortilla chips and cheese"

    Recipe.new(name="nachos", instructions=old_instructions).save()

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


def test_delete(s3):
    Recipe.new(name="nachos", instructions="Melt cheese on chips").save()

    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    assert len(response["Contents"]) == 1
    assert response["Contents"][0]["Key"] == "nachos"

    Recipe.delete("nachos")

    # Data in S3 is gone after deleting the recipe
    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    assert "Contents" not in response.keys()
