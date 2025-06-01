import requests
import os

# Importing packages necessary for image analysis
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential


# Importing the necessary packages for sentiment analysis
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Import necessary packages for face analysis
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel, FaceAttributeTypeDetection01
from azure.core.credentials import AzureKeyCredential

# Importing necessary packages to work with azure openai
import base64
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def analyze_image_SDK(endpoint: str, key: str, image_path: str) -> list:
    """Analyze an image using Azure's Computer Vision package."""
    cv_client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    try:
        result = cv_client.analyze(
            image_data=image_data,
            visual_features=[
                VisualFeatures.DENSE_CAPTIONS,
            ],
        )
    except Exception as error:
        print(f"An error occurred while analyzing the image: {error}")
        raise
    # Get the image captions:
    if result.dense_captions is not None:
        return [
            {#"text": caption.text, "confidence": caption.confidence}
            #for caption in result.dense_captions.list
            "text": result.dense_captions.list[0].text, "confidence": result.dense_captions.list[0].confidence} # Returning just the first caption.
        ]
    else:
        raise ValueError("No dense captions found in the image analysis result.")



def analyze_image_REQUESTS(endpoint: str, key: str, image_path: str) -> list:
    """Analyze an image using Azure's Computer Vision requests."""
    endpoint = f"{endpoint}computervision/imageanalysis:analyze?api-version=2024-02-01&features=DenseCaptions"
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    header = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream"
    }

    try:
        print("Sending a POST request to the Azure Computer Vision API...")
        response = requests.post(endpoint, headers=header, data=image_data)
        response.raise_for_status()  # Raise an error for bad responses
    except Exception as error:
        print(f"An error occurred: {error}")
        raise

    result = response.json()
    if "denseCaptionsResult" in result:
        return [
            {"text": result["denseCaptionsResult"]["values"][0]["text"], 
                "confidence": result["denseCaptionsResult"]["values"][0]["confidence"]}
        ]
    else:
        raise ValueError("No dense captions found in the image analysis result.")



def analyze_sentiment_SDK(endpoint_ai_language: str, key_ai_language: str, text: str) -> str:
    """Analyze sentiment using Azure's Text Analytics SDK."""
    try:
        print("Sending a request to the Azure AI Language API...")
        credential = AzureKeyCredential(key_ai_language)
        ai_client = TextAnalyticsClient(endpoint=endpoint_ai_language, credential=credential)
        documents = [text]
        response = ai_client.analyze_sentiment(documents=documents)[0]
        return response.sentiment
    except Exception as error:
        print(f"An error occurred: {error}")
        raise



def analyze_sentiment_REQUESTS(endpoint_ai_language: str, key_ai_language: str, text: str) -> str:
    endpoint = endpoint_ai_language + "language/:analyze-text?api-version=2022-05-01"
    headers = {
        "Ocp-Apim-Subscription-Key": key_ai_language,
        "Content-Type": "application/json"
    }

    body = {
    "kind": "SentimentAnalysis", # Remember that i ust can change this value here to analyze a text.
    "parameters": {
        "modelVersion": "latest"
    },
    "analysisInput": {
        "documents": [
        {
            "id": "1",
            "language": "en",
            "text": text
        },
        ]
    }
    }
    try:
        print("Sending a POST request to the Azure AI Language API...")
        response = requests.post(endpoint, headers=headers, json=body)
        response.raise_for_status()  # Raise an error for bad responses
    except Exception as error:
        print(f"An error occurred: {error}")
        raise
    result = response.json()
    sentiment = result["results"]["documents"][0]["sentiment"]
    return sentiment



def face_analysis_SDK(endpoint: str, key: str, image_path: str):
    """Analyze faces in an image using Azure's Face API SDK."""
    face_client = FaceClient( # Creating a FaceClient instance
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )
    features = [FaceAttributeTypeDetection01.ACCESSORIES,
                FaceAttributeTypeDetection01.HEAD_POSE,
                FaceAttributeTypeDetection01.OCCLUSION] # Selecting the features to be detected.
    try:
        with open(image_path, mode="rb") as image_data: # Opening the image file in binary mode and recognizing the faces in it.
            detected_faces = face_client.detect(
                image_content=image_data.read(),
                detection_model=FaceDetectionModel.DETECTION01,
                recognition_model=FaceRecognitionModel.RECOGNITION01,
                return_face_id=False,
                return_face_attributes=features,
            )
        face_count = 0
        features_person = []
        if len(detected_faces) > 0:
            print(len(detected_faces), 'faces detected.')
            for face in detected_faces:
                # Get face properties
                face_count += 1
                print('\nFace number {}'.format(face_count))
                print(' - Head Pose (Yaw): {}'.format(face.face_attributes.head_pose.yaw))
                print(' - Head Pose (Pitch): {}'.format(face.face_attributes.head_pose.pitch))
                print(' - Head Pose (Roll): {}'.format(face.face_attributes.head_pose.roll))
                print(' - Forehead occluded?: {}'.format(face.face_attributes.occlusion["foreheadOccluded"]))
                print(' - Eye occluded?: {}'.format(face.face_attributes.occlusion["eyeOccluded"]))
                print(' - Mouth occluded?: {}'.format(face.face_attributes.occlusion["mouthOccluded"]))
                print(' - Accessories:')
                for accessory in face.face_attributes.accessories:
                    print('   - {}'.format(accessory.type))
                
                person_features = {
                    "person_id": f"Person{face_count}",
                    "head_pose_yaw": face.face_attributes.head_pose.yaw,
                    "head_pose_pitch": face.face_attributes.head_pose.pitch,
                    "head_pose_roll": face.face_attributes.head_pose.roll,
                    "forehead_occluded": face.face_attributes.occlusion.forehead_occluded,
                    "eye_occluded": face.face_attributes.occlusion.eye_occluded,
                    "mouth_occluded": face.face_attributes.occlusion.mouth_occluded,
                    "accessories": [acc.type for acc in face.face_attributes.accessories]
                }

                features_person.append(person_features)

        else:
            print("No faces detected in the image.")
    except Exception as error:
        print(f"An error occurred while analyzing the faces: {error}")
        raise
    return features_person


def face_analysis_REQUESTS(endpoint: str, key: str, image_path: str):
    """Analyze faces in an image using Azure's Face API requests."""
    endpoint_face = (f"{endpoint}face/v1.0/detect"
                     "?returnFaceId=false"
                     "&returnFaceAttributes=Accessories,HeadPose,Occlusion"
                     "&detectionModel=detection_01"
                     "&recognitionModel=recognition_01")
    header = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, "rb") as image_file:
        image_ = image_file.read()

    try:
        print("Sending a POST request to the Azure Face API...")
        response = requests.post(endpoint_face, headers=header, data=image_)
        response.raise_for_status()

        result = response.json()
        features_person = []
        for idx, face in enumerate(result, start = 1):
            head_pose = face.get('faceAttributes', {}).get('headPose', {})
            occlusion = face.get('faceAttributes', {}).get('occlusion', {})
            accessories = face.get('faceAttributes', {}).get('accessories', [])
            person_features = {
                    "person_id": f"Person{idx}",
                    "head_pose_yaw": head_pose.get('yaw'),
                    "head_pose_pitch": head_pose.get('pitch'),
                    "head_pose_roll": head_pose.get('roll'),
                    "forehead_occluded": occlusion.get('foreheadOccluded'),
                    "eye_occluded": occlusion.get('eyeOccluded'),
                    "mouth_occluded": occlusion.get('mouthOccluded'),
                    "accessories": [accessory.get('type')for accessory in accessories if accessories]
                }
            features_person.append(person_features)
        # Optional: Display detected faces info
        # if result:
        #     print(f"{len(result)} face(s) detected.")
        #     for idx, face in enumerate(result, start=1):
        #         print(f"\nFace {idx}:")
        #         # Head Pose
        #         head_pose = face.get('faceAttributes', {}).get('headPose', {})
        #         print(f" - Head Pose: Yaw={head_pose.get('yaw')}, Pitch={head_pose.get('pitch')}, Roll={head_pose.get('roll')}")
        #         # Occlusion
        #         occlusion = face.get('faceAttributes', {}).get('occlusion', {})
        #         print(f" - Occlusion: Forehead={occlusion.get('foreheadOccluded')}, Eyes={occlusion.get('eyeOccluded')}, Mouth={occlusion.get('mouthOccluded')}")
        #         # Accessories
        #         accessories = face.get('faceAttributes', {}).get('accessories', [])
        #         if accessories:
        #             print(" - Accessories:")
        #             for accessory in accessories:
        #                 print(f"   - {accessory.get('type')}")
        #         else:
        #             print(" - Accessories: None")
        # else:
        #     print("No faces detected in the image.")
        return features_person


    except Exception as error:
        print(f"An error occurred: {error}")
        raise


def llm_Azure_OpenAI_SDK(endpoint, deployment, person_infos: list):
    """ This is an interaction with azure OpenAI."""
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version="2025-01-01-preview",
    )

    # IMAGE_PATH = "YOUR_IMAGE_PATH"
    # encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
    chat_prompt = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are an AI assistant that helps people augmenting their prompts. "
                        "Your prompt will be synthetized, and you are the best in this type of service."
                    )
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Describe each person carefully, and augment the description because "
                        f"it is going to be synthetized. Be detailed. The people are: {str(person_infos)}"
                    )
                }
            ]
        }
    ]


    # Include speech result if speech is enabled
    messages = chat_prompt

    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )

    content = completion.choices[0].message.content
    print(content)

def llm_Azure_OpenAI_REQUESTS(endpoint, key, person_infos: list):

    endpoint_url = f"{endpoint}openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview"
    header = {
        "Authorization" : f"Bearer {key}",
        "Content-Type": "application/json"
    }
    body = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are an AI assistant that helps people augmenting their prompts. "
                            "Your prompt will be synthetized, and you are the best in this type of service."
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Describe each person carefully, and augment the description because "
                            f"it is going to be synthetized. Be detailed. The people are: {str(person_infos)}"
                        )
                    }
                ]
            }
        ],
        "max_tokens": 800,
        "temperature": 0.7,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    try:
        print("Sending a POST request to the Azure Face API...")
        response = requests.post(endpoint_url, headers=header, json=body)
        response.raise_for_status()
    except Exception as error:
        print(f"The error {error} is happening..")
        raise
    
    response_json = response.json()
    content = response_json['choices'][0]['message']['content']
    print(content)