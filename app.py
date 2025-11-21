import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile

# -----------------------------------------
# Load Azure Speech Key + Region
# -----------------------------------------
# Put your API key here ONLY for testing
# SAFER: export as environment variable:
#
#   export AZURE_SPEECH_KEY="yourkey"
#   export AZURE_SPEECH_REGION="yourregion"
#
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "1f9hcUtjhvtdUv2nhtebXYAQ2SaWu8MjEyrZ0hH37jw1n4ETfgXVJQQJ99BKAC3pKaRXJ3w3AAAYACOG3AV4")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "YOUR_REGION")

# -----------------------------------------
# Streamlit UI
# -----------------------------------------
st.title("Azure Speech-To-Text & Text-To-Speech Translator")
st.write("Upload audio → Transcribe → Translate → Generate speech")

uploaded_file = st.file_uploader("Upload WAV file", type=["wav"])
input_text = st.text_area("Or type text here (for Text → Speech)")
from_lang = st.text_input("Speech Recognition Language", "en-US")
to_lang = st.text_input("Target Language Code", "fr")
voice_name = st.text_input("Voice Name (example: fr-FR-HenriNeural)", "fr-FR-HenriNeural")

# -----------------------------------------
# Speech-To-Text
# -----------------------------------------
if st.button("Convert Speech → Text"):
    if uploaded_file is None:
        st.error("Please upload a WAV file first")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_file.read())
            wav_path = tmp.name

        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        st.info("Transcribing...")
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            st.success("Transcription Successful!")
            st.write("**Recognized Text:**")
            st.write(result.text)
        else:
            st.error("Failed to transcribe audio.")

# -----------------------------------------
# Text-To-Speech
# -----------------------------------------
if st.button("Convert Text → Speech"):
    if input_text.strip() == "":
        st.error("Type some text first!")
    else:
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = voice_name

        out_file = "tts_output.wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=out_file)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        st.info("Generating speech...")
        result = synthesizer.speak_text(input_text)

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            st.success("Speech generated!")

            audio_bytes = open(out_file, "rb").read()
            st.audio(audio_bytes, format="audio/wav")
        else:
            st.error("Text-to-speech failed.")

# -----------------------------------------
# (Optional) Translate Text → Speech
# -----------------------------------------
if st.button("Translate Text → Speech"):
    if input_text.strip() == "":
        st.error("Please enter text first")
    else:
        import requests
        endpoint = "https://api.cognitive.microsofttranslator.com/translate"
        params = {"api-version": "3.0", "to": to_lang}

        headers = {
            "Ocp-Apim-Subscription-Key": SPEECH_KEY,
            "Ocp-Apim-Subscription-Region": SPEECH_REGION,
            "Content-type": "application/json",
        }

        body = [{"text": input_text}]
        r = requests.post(endpoint, params=params, headers=headers, json=body)

        translated_text = r.json()[0]["translations"][0]["text"]
        st.success("Translated Text:")
        st.write(translated_text)

        # Now convert translated text to speech
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = voice_name

        out_file = "translated_speech.wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=out_file)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        st.info("Generating translated speech...")
        result = synthesizer.speak_text(translated_text)

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            st.success("Translated speech generated!")

            audio_bytes = open(out_file, "rb").read()
            st.audio(audio_bytes, format="audio/wav")
        else:
            st.error("Synthesis failed.")
