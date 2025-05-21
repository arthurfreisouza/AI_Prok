""" This module contains functions to create Azure functions. """
import requests
import azure.cognitiveservices.speech as speechsdk



def sentiment_analysis(text, endpoint, key):
    """
    Sentiment Analysis function.
    """
    
    url = endpoint + "language/:analyze-text?api-version=2022-05-01"

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": key,
    }

    body = {
        "kind": "SentimentAnalysis",
        "parameters": {
            "modelVersion": "latest"
        },
        "analysisInput": {
            "documents": [
                {
                    "id": "1",
                    "language": "en",
                    "text": text,
                }
            ]
        }
    }
    try:
        result = requests.post(url, headers = headers, json = body)
        result.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise
    return result


def text_to_speech(text, key, region, output_filename = "output_audio.wav"):
    try:
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region) # This is the correct way to set up the speech configuration
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename) # This is the correct way to set up the audio configuration
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural" # This is the correct way to set the voice name
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