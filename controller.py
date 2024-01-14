import keyboard
import json
import requests
from app import user_input, talk

ngrok = "http://127.0.0.1:5000/"

print("test 1")
setup()
print("test 2")
main()
print("test 3")
getHTML("https://github.com/iankorovinsky")
print("test 4")


def test():
    url = ngrok
    response = requests.get(url)

def speak():
    text = user_input()
    teddy_text = generate_response(text)
    talk(teddy_text)
    print("Done sequence.")

def capture():
    url = ngrok + "capture"
    response = requests.get(url)
    print(response.json())

# Map arrow keys to corresponding functions
key_mapping = {
    "m": speak,
    "t": capture
}

try:
    print("Press arrow keys to execute code. Press 'Esc' to exit.")

    while True:
        key_event = keyboard.read_event(suppress=True)
        if key_event.event_type == keyboard.KEY_DOWN:
            if key_event.name == "esc":
                break  # Exit the program if 'Esc' is pressed

            # Execute code based on the arrow key pressed
            action = key_mapping.get(key_event.name)
            if action:
                action()

except KeyboardInterrupt:
    pass
finally:
    keyboard.unhook_all()