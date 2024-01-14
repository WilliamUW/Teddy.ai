import sounddevice as sd
import soundfile as sf
import keyboard
import queue
import threading
import time
import os

# Parameters for audio recording
samplerate = 44100  # Sample rate in Hertz
channels = 2        # Number of audio channels
filename = f'output{time.time()}.wav'  # Filename to save the audio

# Create a queue to hold the audio data
q = queue.Queue()

# Flag to control recording state
recording = True

def audio_callback(indata, frames, time, status):
    """Callback function for audio recording."""
    if status:
        print(status)
    q.put(indata.copy())

def record_audio():
    """Function to record audio."""
    global recording
    try:
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=audio_callback):
            with sf.SoundFile(filename, mode='x', samplerate=samplerate, channels=channels) as file:
                print('Recording... Press "q" to stop.')
                while recording:
                    file.write(q.get())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print('Recording has been stopped.')
        # Ensure the stream is stopped
        sd.stop()

def stop_recording():
    """Function to stop recording."""
    global recording
    recording = False

def main_audio():
    global filename
    global recording
    filename = f'output{time.time()}.wav'
    # Start the recording in a separate thread
    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

    # Set a hook for the 'q' key to stop recording
    keyboard.add_hotkey('q', stop_recording)

    # Wait for the recording thread to finish
    recording_thread.join()

    # Additional wait to ensure the file is released
    time.sleep(1)
    recording = True
    print('Recording stopped. Audio saved to:', filename)
    return filename