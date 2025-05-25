import azure.cognitiveservices.speech as speechsdk


def create_speech_synthesizer(speech_key, service_region, voice="pt-BR-FranciscaNeural"):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = voice
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    return synthesizer


def speak_text(text, synthesizer):
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("✔️ Speech synthesized successfully.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"❌ Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")


def translation_with_tts(speech_key, service_region):
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=speech_key, region=service_region
    )
    translation_config.speech_recognition_language = "en-US"
    translation_config.add_target_language("pt")

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config, audio_config=audio_config
    )

    synthesizer = create_speech_synthesizer(speech_key, service_region)

    def recognized_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            print(f"🎙️ Recognized: {evt.result.text}")
            translated = evt.result.translations["pt"]
            print(f"🌍 Translated: {translated}")
            speak_text(translated, synthesizer)

    recognizer.recognized.connect(recognized_callback)

    recognizer.canceled.connect(lambda evt: print(f"❌ Canceled: {evt}"))

    print("🎧 Speak in English... (Ctrl+C to stop)")
    recognizer.start_continuous_recognition()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        recognizer.stop_continuous_recognition()
        print("🛑 Recognition stopped.")


# # 🚀 Run the program
# if __name__ == "__main__":
#     speech_key = "BiTL1Fve3YibMTqclQPp25s2JMmots3uygtp1sM0EtaIxWXTAWAEJQQJ99BEAC4f1cMXJ3w3AAAYACOGdK0S"
#     service_region = "westus"

#     translation_with_tts(speech_key, service_region)
