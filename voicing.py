from elevenlabs import generate, stream, set_api_key
import os
import dotenv
dotenv.load_dotenv()

set_api_key(os.getenv('ELEVENLABS_API_KEY'))

def play_voice(text):
    audio_stream = generate(
        text=text,
        voice="Gigi",
        stream=True
    )
    stream(audio_stream)