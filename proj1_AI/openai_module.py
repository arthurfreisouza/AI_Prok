""" This module contains functions to create an OpenAI client. """
from openai import OpenAI
import base64


def creating_openai_client(openai_api_key):
    """
    Create an OpenAI client using the provided API key.
    """
    try:
        client = OpenAI(api_key = openai_api_key)
        if not client:
            print("Failed to create OpenAI client.")
        else:
            print("OpenAI client created successfully.")

    except Exception as error:
        print(f"Error creating OpenAI client: {error}")
        raise
    return client


def generate_image(client, prompt):
    """
    Generate an image using the OpenAI client and the provided prompt.
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd",
            style="natural",
            response_format="b64_json",  # REQUIRED if you want base64 output
        )

        # Access response directly as a Python object
        image_base64 = response.data[0].b64_json  # No .json()

        image_bytes = base64.b64decode(image_base64)

        # Save the image to a file
        with open("sprite.png", "wb") as f:
            f.write(image_bytes)

    except Exception as error:
        print(f"Error generating image: {error}")
        raise