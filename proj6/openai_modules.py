import os
import base64
import requests
from openai import OpenAI



def calling_LLM_SDK(key_openai: str, text: str, model_name: str = "gpt-4o-mini"):
    """Call the OpenAI LLM using the SDK."""
    client = OpenAI(api_key=key_openai)
    completion = client.chat.completions.create(
        model = model_name,
        messages = [
            {"role": "developer", "content": "You are a helpful assistant specialized in enhancing and expanding prompts for image generation. Your task is to analyze the following short text and transform it into a more descriptive, vivid, and detailed prompt suitable for generating high-quality images. Ensure the result emphasizes elements related to science and technology."},
            {"role": "user", "content": text},
        ]
    )
    return completion.choices[0].message.content

def calling_LLM_REQUESTS(endpoint_openai: str, key_openai: str, text: str, model_name: str = "gpt-4o-mini"):
    """Call the OpenAI LLM using the SDK."""
    endpoint_url = f"{endpoint_openai}chat/completions"
    header = {
        "Authorization": f"Bearer {key_openai}",
        "Content-Type": "application/json"
    }

    body = {
    "model": model_name,
    "messages": [
        {
        "role": "developer", "content": "You are a helpful assistant specialized in enhancing and expanding prompts for image generation. Your task is to analyze the following short text and transform it into a more descriptive, vivid, and detailed prompt suitable for generating high-quality images. Ensure the result emphasizes elements related to science and technology."},
        {"role": "user", "content": text
        }
    ],
    "temperature": 0.7
    }
    try:
        print("Sending a POST request to the OpenAI API...")
        response = requests.post(endpoint_url, headers=header, json=body)
        response.raise_for_status()  # Raise an error for bad responses
    except Exception as error:
        print(f"An error occurred: {error}")
        raise
    result = response.json()
    return result["choices"][0]["message"]["content"]


def calling_IMG_GEN_SDK(key_openai: str, text: str, model_name: str = "dall-e-3"):
    """Call the OpenAI DALL·E 3 model using the SDK and save the image."""
    try:
        client = OpenAI(api_key=key_openai)

        completion = client.images.generate(
            model = model_name,
            prompt = text,
            n = 1,
            size = "1024x1024",
            quality = "hd",
            style = "natural",
        )

        image_url = completion.data[0].url
        print(f"Image URL: {image_url}")

        # Download the image from the URL (is not a synchronous operation)
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = response.content

    except Exception as error:
        print(f"An error occurred while generating or downloading the image: {error}")
        raise

    print("Saving the image in outputs/output.png")
    os.makedirs("outputs", exist_ok=True)

    with open("outputs/output.png", "wb") as f:
        f.write(image_bytes)

    print("Image saved successfully.")

def calling_IMG_GEN_REQUESTS(endpoint_openai: str, key_openai: str, text: str, model_name: str = "dall-e-3"):
    """Call the OpenAI LLM using the SDK."""
    header = {
        "Authorization": f"Bearer {key_openai}",
        "Content-Type": "application/json"
    }
    endpoint_url = f"{endpoint_openai}images/generations"
    
    body = {
        "model": model_name,
        "prompt": text,
        "n": 1,
        "size": "1024x1024",
        "quality": "hd",
        "style": "natural"
    }
    try:
        print("Sending a POST request to the OpenAI API...")
        response = requests.post(endpoint_url, headers=header, json=body)
        response.raise_for_status()  # Raise an error for bad responses
    except Exception as error:
        print(f"An error occurred: {error}")
        raise
    result = response.json()
    image_url = result["data"][0]["url"]
    print(f"Image URL: {image_url}")

    try:
        response = requests.get(image_url) # Taking the image(get)
        response.raise_for_status()  # Raise an error for bad responses
        image_bytes = response.content
    except Exception as error:
        print(f"An error occurred while downloading the image: {error}")
        raise
    print("Saving the image in outputs/output.png")
    os.makedirs("outputs", exist_ok=True)

    with open("outputs/output.png", "wb") as f:
        f.write(image_bytes)

    print("Image saved successfully.")