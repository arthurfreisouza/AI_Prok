""" This is the main file for the project. It will be used to run the project. """
import os
import sys
from dotenv import load_dotenv, find_dotenv
from azure_modules import (analyze_image_SDK, 
                           analyze_image_REQUESTS,
                           analyze_sentiment_SDK,
                           analyze_sentiment_REQUESTS,
                           face_analysis_SDK,
                           face_analysis_REQUESTS,
                           llm_Azure_OpenAI_SDK,
                           llm_Azure_OpenAI_REQUESTS)
from openai_modules import (calling_LLM_SDK, 
                            calling_LLM_REQUESTS, 
                            calling_IMG_GEN_SDK, 
                            calling_IMG_GEN_REQUESTS)


def load_environment_variables(PATH: str = ".env"):
    """Load environment variables from .env file."""

    try:
        load_dotenv(find_dotenv(PATH))
        print("Environment variables loaded successfully.")
        endpoint_computer_vision = os.getenv("ENDPOINT_COMPUTER_VISION")
        key_computer_vision = os.getenv("KEY_COMPUTER_VISION")
        endpoint_ai_language = os.getenv("ENDPOINT_AI_LANGUAGE")
        key_ai_language = os.getenv("KEY_AI_LANGUAGE")
        endpoint_openai = os.getenv("ENDPOINT_OPENAI")
        key_openai = os.getenv("KEY_OPENAI")
        endpoint_face = os.getenv("ENDPOINT_FACE")
        key_face = os.getenv("KEY_FACE")
        endpoint_azure_openai = os.getenv("ENDPOINT_AZURE_OPENAI")
        key_azure_openai = os.getenv("KEY_AZURE_OPENAI")
    except Exception as error:
        print(f"Error loading environment variables: {error}")
        raise
    return endpoint_computer_vision, key_computer_vision, endpoint_ai_language, key_ai_language, endpoint_openai, key_openai, endpoint_face, key_face, endpoint_azure_openai, key_azure_openai


def process_option() -> int:
    """Process the user's option."""
    print("Processing option...")
    option = 0
    while option == 0:
        try:
            option = int(input("Enter your option (1-4): "))
            if option < 1 or option > 4:
                print("Invalid option. Please try again.")
                option = 0
        except Exception as error:
            print(f"The error has been generated: {error}")
            raise
    print(f"You have chosen option {option}.")
    return option


def calling_services(choosed_option: int, env_variables: dict = None, image_path: str = "images/default.jpeg"):
    """Call the appropriate service based on the user's choice."""
    
    while choosed_option in [1,2,3,4]:
        ########################################################################################################################################################################################################################
        if choosed_option == 1:
            print("You have chosen option 1: Analyze an image and generate a new image based on sentiment.")
            ########################### Analyzing the image and providing a dense_captions.  ###########################
            endpoint_image_analysis = env_variables.get("endpoint_computer_vision")
            key_image_analysis = env_variables.get("key_computer_vision")
            #result = analyze_image_SDK(key_image_analysis, endpoint_image_analysis, image_path)
            result = analyze_image_REQUESTS(key_image_analysis, endpoint_image_analysis, image_path)
            extracted_text = result[0]['text']
            print(f"Extracted text from image: {extracted_text}")
            ############################################################################################################



            ########################### Analyzing the dense captions and providing a the sentiment.  #####################
            endpoint_ai_language = env_variables.get("endpoint_ai_language")
            key_ai_language = env_variables.get("key_ai_language")
            #analyzed_sentiment = analyze_sentiment_SDK(endpoint_ai_language = endpoint_ai_language, key_ai_language = key_ai_language, text = extracted_text) # Return
            analyzed_sentiment = analyze_sentiment_REQUESTS(endpoint_ai_language = endpoint_ai_language, key_ai_language = key_ai_language, text = extracted_text) # Return
            print(f"Sentiment analysis result: {analyzed_sentiment}")
            ############################################################################################################



            ########################### Augmenting the prompt with a large language model, to create a better image.  #####################
            endpoint_openai = env_variables.get("endpoint_openai")
            key_openai = env_variables.get("key_openai")
            #augmented_text = calling_LLM_SDK(key_openai = key_openai, text = extracted_text) # Return
            augmented_text = calling_LLM_REQUESTS(endpoint_openai = endpoint_openai, key_openai = key_openai, text = extracted_text) # Return
            print(f"Augmented text for image generation: {augmented_text}")
            ############################################################################################################




            ########################### Feeding the generated image.  #####################
            #calling_IMG_GEN_SDK(key_openai = key_openai, text = augmented_text) # Return
            calling_IMG_GEN_REQUESTS(endpoint_openai = endpoint_openai, key_openai = key_openai, text = augmented_text) # Return
            
            ############################################################################################################

        ########################################################################################################################################################################################################################

        elif choosed_option == 2:
            print("You have chosen option 2: Analyze the features of the image and synthesize a song's lyrics.")

            ########################### Taking a list of detected people, and their attributes.  #####################
            endpoint_ai_face = env_variables.get("endpoint_face")
            key_ai_face = env_variables.get("key_face")
            #returned_faces = face_analysis_SDK(endpoint = endpoint_ai_face, key = key_ai_face, image_path ="images/faces.jpg")
            returned_faces = face_analysis_REQUESTS(endpoint = endpoint_ai_face, key = key_ai_face, image_path ="images/faces.jpg")
            print(f"The returned faces are{returned_faces}, and the type: {type(returned_faces)}")
            ########################################################################################################################################################################################################################

             ########################### Asking a LLM from azure to describe each person, generating an augmented prompt.  #####################
            endpoint_azure_openai = env_variables.get("endpoint_azure_openai")
            key_azure_openai = env_variables.get("key_azure_openai")
            #llm_Azure_OpenAI_SDK(endpoint = endpoint_azure_openai, deployment = "gpt-4o-mini", person_infos = returned_faces)
            llm_Azure_OpenAI_REQUESTS(endpoint = endpoint_azure_openai, key = key_azure_openai, person_infos = returned_faces)
            ########################################################################################################################################################################################################################

            ########################### Generating a speech (synthetizer), describing each person.  #####################
            ########################################################################################################################################################################################################################
        elif choosed_option == 3:
            print("You have chosen option 3: Analyze a document and generate an image based on important words.")
            # Here you would implement the logic for option 3
        elif choosed_option == 4:
            print("You have chosen option 4: Exit the program.")
            break
        else:
            print("Invalid option. Please try again.")
            choosed_option = process_option()
        choosed_option = int(input("Enter your option (1-4): "))

def main():
    endpoint_computer_vision, key_computer_vision, endpoint_ai_language, key_ai_language, endpoint_openai, key_openai, endpoint_face, key_face, endpoint_azure_openai, key_azure_openai = load_environment_variables()
    env_variables = {
        "endpoint_computer_vision": endpoint_computer_vision,
        "key_computer_vision": key_computer_vision,
        "endpoint_ai_language": endpoint_ai_language,
        "key_ai_language": key_ai_language,
        "endpoint_openai": endpoint_openai,
        "key_openai": key_openai,
        "endpoint_face": endpoint_face,
        "key_face": key_face,
        "endpoint_azure_openai": endpoint_azure_openai,
        "key_azure_openai": key_azure_openai,
    }
    print("Select an option:")
    print("1. Analyze an image the sentiment of an image, if positive give a prompt to a model and generate an image using dalle or image1, if sad creates a sad image using dalle or image1.")
    print("2. Analyze the features of the image, and if there is a glass ask me a song's name and synthetize the letter of the song in another language [just in one another language].")
    print("3. Send me a document path, and use the DI to find the most important words in the document, and then generate an image using dalle or image1.")
    print("4. Exit the program.")
    choosed_option = process_option()
    image_path = "images/default.jpeg"  # Default image path if not provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    calling_services(choosed_option = choosed_option, env_variables = env_variables, image_path = image_path)
    print("Thank you for using the program. Goodbye!")


if __name__ == "__main__":
    main()