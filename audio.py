from elevenlabs import generate, stream

audio_stream = generate(
  text="What's up dog!!!!",
  voice="Gigi",
  stream=True
)

stream(audio_stream)