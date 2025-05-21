from azure.cognitiveservices.vision.computervision import ComputerVisionClient# This is the client for the Computer Vision API.
from msrest.authentication import CognitiveServicesCredentials # This is used to authenticate your request using the subscription key.
import azure.cognitiveservices.speech as speechsdk
import time
import uuid
import requests





def generate_translation(translator_key, translator_endpoint, region, text):
    # Endpoint for translation
    path = 'translate'
    constructed_url = translator_endpoint + path
    params = {
        'api-version': '3.0',
        'from': 'en',             # Source language (optional)
        'to': ['pt', 'es']        # Target languages (Portuguese and Spanish here)
    }
    headers = {
        "Ocp-Apim-Subscription-Key": translator_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{
        'text': text,
    }]
    try:
        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        response = request.json()
        request.raise_for_status()
    except Exception as error:
        print(f"The error {error} has happened.")
    return response

def applying_ocr(image_path, ocr_key, ocr_endpoint):
    """
    Apply OCR to the image using Azure Computer Vision API.

    Args:
        image_path (str): Path to the local image file.
        ocr_key (str): Azure Computer Vision subscription key.
        ocr_endpoint (str): Azure endpoint URL.

    Returns:
        list: List of extracted text lines.
    """
    try:
        # Create client to acess the computer vision service.
        computervision_client = ComputerVisionClient(
            ocr_endpoint, CognitiveServicesCredentials(ocr_key)
        )

        # Open image as binary and read the image using computer vision.
        with open(image_path, "rb") as image_stream:
            print("Submitting image for OCR...")
            read_response = computervision_client.read_in_stream(image_stream, raw=True)

        # Get operation ID from the response
        operation_location = read_response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        # Polling for result
        print("Waiting for OCR results...")
        while True:
            read_result = computervision_client.get_read_result(operation_id) # Get the result of the read operation with the operation ID.
            if read_result.status.lower() not in ["notstarted", "running"]:
                break
            time.sleep(1)

        # Extract text if succeeded
        extracted_text = []
        if read_result.status == "succeeded":
            for page in read_result.analyze_result.read_results:
                for line in page.lines:
                    extracted_text.append(line.text)
                    print(line.text)

        return extracted_text

    except Exception as error:
        print(f"Error applying OCR: {error}")
        raise
    


def text_to_speech(text, key, region, output_filename = "output_audio.wav", voice_name = "en-US-JennyNeural"):
    try:
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region) # This is the correct way to set up the speech configuration
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename) # This is the correct way to set up the audio configuration
        speech_config.speech_synthesis_voice_name = voice_name # This is the correct way to set the voice name
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized for text [{text}]")
        else:
            print(f"Speech synthesis canceled, reason: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"CancellationDetails.ErrorDetails: {cancellation_details.error_details}")
    except Exception as error:
        print(f"Error synthesizing speech: {error}")
        raise