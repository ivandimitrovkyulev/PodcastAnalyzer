from os import path
from googletrans import Translator
import speech_recognition as sr


filename = "audio.wav"
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), filename)

# Pass audio file and construct the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)

# use Google Speech Recognition to recognize the voice
try:
    transcript = r.recognize_google(audio)
except sr.UnknownValueError:
    print("Audio file could not be understood.")
except sr.RequestError as e:
    print(f"Results could not be requested from Google Speech Recognition service; {e}")


print(transcript)