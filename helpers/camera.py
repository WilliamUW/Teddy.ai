import cv2

def capture_photo(camera_index=0, save_path='captured_photo.jpg'):
    # Open the camera
    cap = cv2.VideoCapture(camera_index)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Capture a single frame
    ret, frame = cap.read()

    # Check if the frame is captured successfully
    if not ret:
        print("Error: Could not capture frame.")
        cap.release()
        return

    # Save the captured frame as an image
    cv2.imwrite(save_path, frame)

    print(f"Photo captured and saved as {save_path}")

    # Release the camera
    cap.release()
    return save_path

