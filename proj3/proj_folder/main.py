from dotenv import load_dotenv, find_dotenv
from azure_functions import calling_image_analysis, calling_translator, POST_speech, GET_speech_token
import os

def loading_environments():
    """ Loading the environments variables from the .env file """

    try:
        print("Loading environment variables...")
        load_dotenv(find_dotenv(".env"))
        endpoint_img_analysis = os.getenv("ENDPOINT_IMG_ANALYSIS")
        key_img_analysis = os.getenv("KEY_IMG_ANALYSIS")
        endpoint_translator = os.getenv("ENDPOINT_AI_TRANSLATOR")
        key_translator = os.getenv("KEY_AI_TRANSLATORS")
        region_translator = os.getenv("REGION_AI_TRANSLATOR")
        endpoint_speech = os.getenv("ENDPOINT_TEXT_TO_SPEECH")
        key_speech = os.getenv("KEY_TEXT_TO_SPEECH")
    except Exception as error:
        print(f"Error loading environment variables: {error}")
        raise
    return endpoint_img_analysis, key_img_analysis, endpoint_translator, key_translator, region_translator, endpoint_speech, key_speech


def main():
    """ Main function to call the Azure Function """

    # Load environment variables
    endpoint_img_analysis, key_img_analysis, endpoint_translator, key_translator, region_translator, endpoint_speech, key_speech = loading_environments()

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Calling the image analysis function
    result_img_analysis = calling_image_analysis(
        endpoint_img_analysis=endpoint_img_analysis,
        key_img_analysis=key_img_analysis,
        img_path="my_image.jpg",
    )
    list_ = []
    for i in result_img_analysis.json()["denseCaptionsResult"]["values"]:
        list_.append(i["text"])
    
    # print(list_)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Calling the translator function

    result_text_translator = calling_translator(
        endpoint_translator = endpoint_translator,
        region_translator = region_translator,
        key_translator = key_translator,
        phrases = list_,)
    print(result_text_translator.json())

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Calling the speech function

    GET_token = GET_speech_token(region = region_translator, subscription_key = key_speech)
    for item in result_text_translator.json():
        count = 0
        if 'translations' in item: # Check if the 'translations' key exists
            for translation_entry in item['translations']: # Iterate through the list of translations
                translated_text = translation_entry.get('text')
                target_language = translation_entry.get('to')
                if translated_text is not None and target_language is not None:
                    # print(f"Language: {target_language}, Text: {translated_text}")
                    results = POST_speech(
                        endpoint_speech = endpoint_speech,
                        language = target_language,
                        access_token = GET_token,
                        text = translated_text,
                    )
                    with open(f"output{count}.mp3", "wb") as audio:
                        audio.write(results.content)
                    count += 1
        break

    else:
        print("Warning: 'translations' key not found in an item.")

if __name__ == "__main__":
    main()