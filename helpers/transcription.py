from openai import OpenAI
import os
import dotenv
dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def transcriber(filename):
    audio_file= open(filename, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    print(f"TRANSCRIPTION: {transcript.text}")
    return transcript.text