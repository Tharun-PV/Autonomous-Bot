import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)
detector = FaceMeshDetector(maxFaces=1)
d = None  # Global variable to store distance


def camera_loop():
    global d
    cap = cv2.VideoCapture("http://192.168.59.57:8080/video")
    while True:
        success, img = cap.read()
        img, faces = detector.findFaceMesh(img, draw=False)

        if faces:
            face = faces[0]
            pointLeft = face[145]
            pointRight = face[374]
            w, _ = detector.findDistance(pointLeft, pointRight)
            W = 6.3

            # Finding distance
            f = 840
            d = (W * f) / w
            print(d)

            cvzone.putTextRect(img, f'Distance: {int(d)}cm',
                               (face[10][0] - 100, face[10][1] - 50),
                               scale=2)
        else:
            d = "null"  # Set distance to None if no faces are detected
            print("null")

        cv2.imshow("Image", img)
        cv2.waitKey(1)


def start_flask_server():
    app.run(host='0.0.0.0', port=5000)


@app.route('/distance', methods=['GET'])
def get_distance():
    global d
    return jsonify({'distance': d})


if __name__ == '__main__':
    camera_thread = Thread(target=camera_loop)
    flask_thread = Thread(target=start_flask_server)

    camera_thread.start()
    flask_thread.start()

    camera_thread.join()
    flask_thread.join()
