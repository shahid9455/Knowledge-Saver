import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import io
import time

# Replace these with your actual credentials
api_key = 'LZIYjqxXb_9SzB__zoKP3B_RsciBfjrlqpeezDC-HbRD'
url = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/ef13fb51-cbd7-488c-83ce-1363fd782882'

# Set up the authenticator and service
authenticator = IAMAuthenticator(api_key)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(url)

# Parameters for recording
sampling_rate = 16000  # Hz
duration = 5  # seconds

# Function to record audio from the microphone
def record_audio(duration, sampling_rate):
    print("Recording...")
    recording = sd.rec(int(duration * sampling_rate), samplerate=sampling_rate, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete.")
    return recording

# Function to save the recording as a WAV file
def save_wav_file(filename, data, sampling_rate):
    write(filename, sampling_rate, data)

# Function to convert audio to text
def transcribe_audio(filename):
    with open(filename, 'rb') as audio:
        response = speech_to_text.recognize(
            audio=audio,
            content_type='audio/wav',
            model='en-US_BroadbandModel'
        ).get_result()

    return response['results'][0]['alternatives'][0]['transcript']

# Record live audio
audio_data = record_audio(duration, sampling_rate)

# Save the recording to a WAV file
filename = 'live_audio.wav'
save_wav_file(filename, audio_data, sampling_rate)

# Transcribe the saved WAV file
text = transcribe_audio(filename)
print("Transcribed Text:")
print(text)
