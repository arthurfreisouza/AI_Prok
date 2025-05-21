from dotenv import load_dotenv, find_dotenv
from azure_modules import applying_ocr, generate_translation, text_to_speech
import os

def load_environment():
    try:
        print("Loading environment...")
        load_dotenv(find_dotenv(".env"))
        ocr_key = os.getenv("KEY_COMPUTER_VISION")
        ocr_endpoint = os.getenv("ENDPOINT_COMPUTER_VISION")
        translator_key = os.getenv("KEY_TRANSLATOR")
        translator_endpoint = os.getenv("ENDPOINT_TRANSLATOR")
        translator_region = os.getenv("REGION_TRANSLATOR")
        speech_endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")
        speech_key = os.getenv("AZURE_SPEECH_KEY")

    except Exception as error:
        print(f"Error loading environment: {error}")
        raise
    return ocr_key, ocr_endpoint, translator_key, translator_endpoint, translator_region, speech_endpoint, speech_key


def main():
    ocr_key, ocr_endpoint, translator_key, translator_endpoint, translator_region, speech_endpoint, speech_key = load_environment()
    region = speech_endpoint.split(".")[0]  # Extract the region from the endpoint
    region = region.split("://")[1]
    # result_ocr = applying_ocr(image_path = "images/test1.jpg", ocr_key = ocr_key, ocr_endpoint = ocr_endpoint)
    result_ocr = applying_ocr(image_path = "images/test2.jpeg", ocr_key = ocr_key, ocr_endpoint = ocr_endpoint)
    # print(f"The result of the OCR is: {result_ocr}")
    total_result = ' '.join([phrase.strip() for phrase in result_ocr])
    print(f"The text extracted in the image is: {total_result}")
    
    translated_text = generate_translation(translator_key = translator_key, translator_endpoint = translator_endpoint,
                                              region = translator_region, text = total_result)
    # print(translated_text)
    translated_pt = translated_text[0]['translations'][0]['text']
    translated_es = translated_text[0]['translations'][1]['text']
    # print(translated_pt)
    # print(translated_es)
    #print(f"The result of translation is: {translated_text}")
    text_to_speech(text = total_result, key = speech_key,
                        region = region,
                        output_filename = "output_en.wav")
    text_to_speech(text = translated_pt, key = speech_key,
                        region = region,
                        output_filename = "output_pt.wav", voice_name = "pt-BR-FranciscaNeural")
    text_to_speech(text = translated_es, key = speech_key,
                        region = region,
                        output_filename = "output_es.wav", voice_name= "es-ES-AlvaroNeural")
    



if __name__ == "__main__":
    main()
