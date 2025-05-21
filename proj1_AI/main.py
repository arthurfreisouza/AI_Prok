from openai_module import creating_openai_client, generate_image
from azure_module import sentiment_analysis, text_to_speech
import requests
import os
from dotenv import load_dotenv, find_dotenv
import sys


PATH = os.path.dirname(os.path.abspath(__file__))
def load_environment_variables():
    """
    Load environment variables from a .env file.
    """
    try:
        load_dotenv(find_dotenv(f"{PATH}/.env"))
        openai_api_key = os.getenv("OPENAI_API_KEY")
        azure_api_key = os.getenv("AZURE_API_KEY")
        azure_endpoint = os.getenv("AZURE_API_ENDPOINT")
        azure_speech_endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")
        azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
    except Exception as error:
        print(f"Error loading environment variables: {error}")
        raise
    return openai_api_key, azure_api_key, azure_endpoint, azure_speech_endpoint, azure_speech_key




def analyzer(str_sentiment, int_sentiment, text, client, azure_api_key, region, azure_speech_key):
    """ This function will analyze the response and call the appropriate model."""
    if str(str_sentiment).lower() == "positive" and int_sentiment >= 0.65:

        prompt = f"""Knowing that my prompt is this one {text} i want you help to augment it before feeding a image generator.
        Could you return the augmented prompt for me, remembering to put as much details as possible to the model and also that i have a positive feeling,
        so the image that i want to generate will transmit good vibes. I want a prompt with a maximum of 250 tokens."""
        augmented_prompt = client.responses.create(
            model="gpt-4.1",
            input=prompt,
        )
        print(f"Augmented prompt: {augmented_prompt.output_text}")
        generate_image(client, augmented_prompt.output_text)

    else:
        # Calling the speech to text function.
        prompt = f"""Knowing that my prompt is this one {text} i want you help to augment it before feeding a text to speech model.
        Could you return the augmented prompt for me, remembering to put as much details as possible to the model and also that i have a negative feeling,
        so the audio that i want to generate will help me in this moment. I want a prompt with a maximum of 250 tokens."""
        augmented_prompt = client.responses.create(
            model="gpt-4.1",
            input=prompt,
        )
        print(f"Augmented prompt: {augmented_prompt.output_text}")
        
        text_to_speech(text = augmented_prompt.output_text, key = azure_speech_key,
                        region = region,
                        output_filename = "output_audio.wav")


def main():
    openai_api_key, azure_api_key, azure_endpoint, azure_speech_endpoint, azure_speech_key = load_environment_variables()
    region = azure_speech_endpoint.split(".")[0]  # Extract the region from the endpoint
    region = region.split("://")[1]
    client = creating_openai_client(openai_api_key)

    text = str(input("Please enter the text you want to analyze: "))
    if not text:
        print("No text provided. Exiting.")
        return
    elif text.lower() == "exit" or text.lower() == "quit":
        print("Exiting the program.")
        return
    analysed_sentiment = sentiment_analysis(text = text, endpoint = azure_endpoint,
                                            key = azure_api_key)
    
    cleaned_sentiment = [analysed_sentiment.json()['results']['documents'][0]['sentiment'],
                         analysed_sentiment.json()['results']['documents'][0]['confidenceScores']['positive'],]
    
    print(f"The sentiment analyzed in the text {text} is: {cleaned_sentiment[0]}")
    
    analyzer(str_sentiment = cleaned_sentiment[0],
            int_sentiment = cleaned_sentiment[1],
            text = text,
            client = client,
            azure_api_key = azure_api_key,
            region = region,
            azure_speech_key = azure_speech_key)
    
    

if __name__ == "__main__":
    main()
