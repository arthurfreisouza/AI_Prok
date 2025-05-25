import requests



def calling_image_analysis(endpoint_img_analysis, key_img_analysis, img_path) -> requests.Response:
    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": key_img_analysis,
    }
    
    with open(img_path, "rb") as image:
        data = image.read()

    try:
        result = requests.post(endpoint_img_analysis, headers=headers, data=data)
        result.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Request failed: {error}")
        raise
    return result


def calling_translator(endpoint_translator, region_translator, key_translator, phrases) -> requests.Response:
    """" This function calls the Azure Translator API to translate a list of phrases into a specified language. """

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": key_translator,
        "Ocp-Apim-Subscription-Region": region_translator,
    }
    
    body = [{"text": phrase} for phrase in phrases]
    
    try:
        result = requests.post(endpoint_translator, headers=headers, json=body)
        result.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Request failed: {error}")
        raise
    return result

def GET_speech_token(region: str, subscription_key: str) -> str:
    """
    Retrieves an authentication token for the Azure Speech Service.
    This token is required for subsequent text-to-speech requests.
    """
    token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    try:
        response = requests.post(token_url, headers=headers)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text # The token is returned as plain text
    except requests.exceptions.RequestException as e:
        print(f"Error getting Speech token: {e}")
        raise # Re-raise to indicate failure to get token


def get_neural_voice_name(language: str = "en-US") -> str:
    """
    Returns a suitable Neural Voice name based on the language.
    """
    # Common Neural Voices (these are high quality)
    voice_map = {
        "en-US": "en-US-GuyNeural",   # English (US) Male
        "pt-BR": "pt-BR-ThalitaNeural", # Portuguese (Brazil) Female
        "es-ES": "es-ES-ElviraNeural", # Spanish (Spain) Female
        "fr-FR": "fr-FR-DeniseNeural", # French (France) Female
        "de-DE": "de-DE-KatjaNeural",  # German (Germany) Female
        # Add more mappings as needed
    }
    return voice_map.get(language) # Default to a common English voice if language not found





def POST_speech(endpoint_speech: str, access_token: str, text: str, language: str) -> requests.Response:
    """
    Calls the Azure Speech API to convert text to speech.

    Args:
        endpoint_speech (str): The Azure Speech Service synthesis endpoint URL.
                                (e.g., "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1")
        access_token (str): The authentication token obtained from the Speech Service.
        text (str): The text content to convert to speech.
        language (str): The BCP-47 language tag (e.g., "en-US", "pt-BR", "es-ES").

    Returns:
        requests.Response: The response object containing the audio data.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
    """
    headers = {
        "Authorization": f"Bearer {access_token}", # Use the acquired token
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3", # High quality MP3
        "User-Agent": "Python-Speech-Client" # Recommended header
    }
    if language == "en":
        language = "en-US"
    elif language == "pt":
        language = "pt-BR"
    elif language == "es":
        language = "es-ES"
    elif language == "fr":
        language = "fr-FR"
    elif language == "de":
        language = "de-DE"
    voice_name = get_neural_voice_name(language)
    print(f"Using voice: {voice_name} for language: {language}")

    # SSML body for text-to-speech
    body = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{language}'>
        <voice name='{voice_name}'>
            <prosody rate='-10.00%' pitch='0%'>
                {text}
            </prosody>
        </voice>
    </speak>
    """
    try:
        result = requests.post(endpoint_speech, headers=headers, data=body.encode('utf-8')) # Encode body to bytes
        result.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as error:
        print(f"Text-to-Speech request failed: {error}")
        raise # Re-raise the exception for upstream handling
    return result
    