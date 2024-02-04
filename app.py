from flask import Flask, render_template, Response, request, jsonify
import cv2
import os
import numpy as np

app = Flask(__name__)

# OpenCV VideoCapture object
cap = cv2.VideoCapture(0)

# Create a folder to store captured frames
output_folder = 'captured_frames'
os.makedirs(output_folder, exist_ok=True)

# Default HSV color ranges
lower_hsv = np.array([150, 90, 0])
upper_hsv = np.array([180, 255, 255])

def create_mask(frame, lower_hsv, upper_hsv, kernel_size=3):
    inspect = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(inspect, lower_hsv, upper_hsv)
    mask = cv2.medianBlur(mask, 3)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=5)

    return mask


first_frame_captured = False

def generate_frames():
    global first_frame_captured
    global lower_hsv, upper_hsv

    # Capture the first frame
    success, frame = cap.read()
    if success and not first_frame_captured:
        # Save the first frame as an image
        image_filename = os.path.join(output_folder, "init_frame.jpg")
        cv2.imwrite(image_filename, frame)

        # Set the flag to True to stop further capturing
        first_frame_captured = True

    init_frame = cv2.imread('captured_frames\init_frame.jpg')

    # Resize init_frame to match the size of the frames from the webcam
    

    if init_frame is not None and init_frame.size != 0:
        # Resize init_frame to match the size of the frames from the webcam
        init_frame = cv2.resize(init_frame, (frame.shape[1], frame.shape[0]))

        while first_frame_captured:
            ret, frame = cap.read()

            mask = create_mask(frame, lower_hsv, upper_hsv)

            mask_inv = 255 - mask

            # Bitwise operations to get the final frame
            frame_inv = cv2.bitwise_and(frame, frame, mask=mask_inv)

            # Bitwise operations to get the blanket area
            blanket_area = cv2.bitwise_and(init_frame, init_frame, mask=mask)

            # Combine the two frames
            final = cv2.bitwise_or(frame_inv, blanket_area)

            # Convert the frame to JPEG
            ret, jpeg = cv2.imencode('.jpg', final)
            if not ret:
                break

            # Yield the frame in bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    global lower_hsv, upper_hsv
    default_values = {
        'lower_hue': lower_hsv[0],
        'lower_saturation': lower_hsv[1],
        'lower_value': lower_hsv[2],
        'upper_hue': upper_hsv[0],
        'upper_saturation': upper_hsv[1],
        'upper_value': upper_hsv[2]
    }
    return render_template('index.html', default_values=default_values)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update_color', methods=['POST'])
def update_color():
    global lower_hsv, upper_hsv

    # Get values from the request
    lower_hsv[0] = int(request.json['lower_hue'])
    lower_hsv[1] = int(request.json['lower_saturation'])
    lower_hsv[2] = int(request.json['lower_value'])
    upper_hsv[0] = int(request.json['upper_hue'])
    upper_hsv[1] = int(request.json['upper_saturation'])
    upper_hsv[2] = int(request.json['upper_value'])

    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True, port=5500)
