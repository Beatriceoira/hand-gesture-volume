import math
import cv2
import numpy as np
import pulsectl

from mediapipe.tasks.python.vision import hand_landmarker
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision.core import image as image_module
from mediapipe.tasks.python.vision.core import vision_task_running_mode
from mediapipe.tasks.python.core import base_options

pulse = pulsectl.Pulse("hand-gesture-volume")
sink = pulse.sink_list()[0]
minVol, maxVol = 0.0, 1.0
volBar, volPer = 400, 0

wCam, hCam = 640, 480
cam = cv2.VideoCapture(1)
cam.set(3, wCam)
cam.set(4, hCam)

model_path = "hand_landmarker.task"
base_options = base_options.BaseOptions(model_asset_path=model_path)
options = hand_landmarker.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision_task_running_mode.VisionTaskRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

with hand_landmarker.HandLandmarker.create_from_options(options) as landmarker:
    while cam.isOpened():
        success, image = cam.read()
        if not success:
            continue

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = image_module.Image(image_module.ImageFormat.SRGB, rgb_image)
        results = landmarker.detect_for_video(mp_image, int(cam.get(cv2.CAP_PROP_POS_MSEC)))

        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                drawing_utils.draw_landmarks(
                    image,
                    hand_landmarks,
                    hand_landmarker.HandLandmarksConnections.HAND_PALM_CONNECTIONS
                    + hand_landmarker.HandLandmarksConnections.HAND_THUMB_CONNECTIONS
                    + hand_landmarker.HandLandmarksConnections.HAND_INDEX_FINGER_CONNECTIONS
                    + hand_landmarker.HandLandmarksConnections.HAND_MIDDLE_FINGER_CONNECTIONS
                    + hand_landmarker.HandLandmarksConnections.HAND_RING_FINGER_CONNECTIONS
                    + hand_landmarker.HandLandmarksConnections.HAND_PINKY_FINGER_CONNECTIONS,
                )

        lmList = []
        if results.hand_landmarks:
            myHand = results.hand_landmarks[0]
            for id, lm in enumerate(myHand):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]

            cv2.circle(image, (x1, y1), 15, (255, 255, 255))
            cv2.circle(image, (x2, y2), 15, (255, 255, 255))
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)

            length = math.hypot(x2 - x1, y2 - y1)
            if length < 50:
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 3)

            vol = np.interp(length, [50, 220], [minVol, maxVol])
            volBar = np.interp(length, [50, 220], [400, 150])
            volPer = np.interp(length, [50, 220], [0, 100])

            pulse.volume_set_all_chans(sink, vol)

            cv2.rectangle(image, (50, 150), (85, 400), (0, 0, 0), 3)
            cv2.rectangle(
                image, (50, int(volBar)), (85, 400), (0, 0, 0), cv2.FILLED
            )
            cv2.putText(
                image,
                f"{int(volPer)} %",
                (40, 450),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (0, 0, 0),
                3,
            )

        cv2.imshow("handDetector", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cam.release()
cv2.destroyAllWindows()
pulse.close()