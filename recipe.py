from dataclasses import dataclass
from io import BytesIO
import json

import boto3

S3_BUCKET = "recipes"


def get_s3():
    return boto3.client("s3")


@dataclass
class Recipe:
    name: str
    instructions: str

    @classmethod
    def get_by_name(cls, name: str):
        """Looks up a Recipe by name
        
        Args:
            name (str): Recipe name
        
        Returns a Recipe object
        """
        response = get_s3().get_object(Bucket=S3_BUCKET, Key=name)
        response = json.loads(response["Body"].read())
        return cls(response["name"], response["instructions"])

    @classmethod
    def update_instructions(cls, name: str, new_instructions: str):
        """Updates the instructions for a recipe
        
        Args:
            name (str): Name of the recipe to update
            new_instructions (str): New instructions
        """
        recipe = cls.get_by_name(name)
        recipe.instructions = new_instructions
        return recipe

    @classmethod
    def delete(cls, name: str):
        """Deletes a recipe
        
        Args:
            name (str): Name of the recipe to delete
        """
        get_s3().delete_object(Bucket=S3_BUCKET, Key=name)

    def to_json(self):
        """Serialized the recipe to json
        
        Returns:
            dict: JSON representation of the Recipe
        """
        return {"name": self.name, "instructions": self.instructions}

    def save(self):
        """Persists a recipe to S3
        """
        serialized_recipe = BytesIO(json.dumps(self.to_json()).encode("utf-8"))
        get_s3().put_object(
            Bucket=S3_BUCKET, Key=self.name, Body=serialized_recipe.getvalue()
        )
