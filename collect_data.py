import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarksConnections
import numpy as np
import pandas as pd
import os

OUTPUT_FILE = "data/dataset.csv"
SAMPLES_PER_SESSION = 200
MODEL_PATH = "hand_landmarker.task"


def get_landmark_array(hand_landmarks):
    landmarks = []
    for lm in hand_landmarks:
        landmarks.extend([lm.x, lm.y, lm.z])
    return np.array(landmarks)


def draw_landmarks_on_frame(frame, landmark_list):
    h, w = frame.shape[:2]
    points = []
    for lm in landmark_list:
        cx, cy = int((1 - lm.x) * w), int(lm.y * h)
        points.append((cx, cy))
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
    for connection in HandLandmarksConnections.HAND_CONNECTIONS:
        start = connection.start
        end = connection.end
        if start < len(points) and end < len(points):
            cv2.line(frame, points[start], points[end], (255, 255, 255), 2)


def main():
    label = input("Enter the letter label (e.g. A): ").strip().upper()
    print(f"Collecting data for letter: {label}")
    print("Press SPACE to start recording. Press Q to quit.")

    cap = cv2.VideoCapture(0)
    recording = False
    samples_collected = 0
    data_rows = []

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = HandLandmarkerOptions(
        base_options=base_options,
        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
    )

    with HandLandmarker.create_from_options(options) as detector:
        timestamp_ms = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # display is flipped for natural viewing
            # frame is unflipped — this is what MediaPipe processes
            display = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            results = detector.detect_for_video(mp_image, timestamp_ms)
            timestamp_ms += 33

            if results.hand_landmarks:
                for hand_landmarks in results.hand_landmarks:
                    draw_landmarks_on_frame(display, hand_landmarks)

                    if recording and samples_collected < SAMPLES_PER_SESSION:
                        landmark_array = get_landmark_array(hand_landmarks)
                        data_rows.append(landmark_array)
                        samples_collected += 1

            status = (
                f"Letter: {label} | Samples: {samples_collected}/{SAMPLES_PER_SESSION}"
            )
            if recording:
                status += " | RECORDING"
            cv2.putText(
                display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )

            cv2.imshow("FSL Data Collection", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(" ") and not recording:
                recording = True
                print("Recording started...")
            elif key == ord("q"):
                break

            if samples_collected >= SAMPLES_PER_SESSION:
                print(f"Done! Collected {samples_collected} samples for '{label}'")
                break

    cap.release()
    cv2.destroyAllWindows()

    if data_rows:
        columns = []
        for i in range(21):
            columns.extend([f"x{i}", f"y{i}", f"z{i}"])

        df = pd.DataFrame(data_rows, columns=columns)
        df["label"] = label

        if os.path.exists(OUTPUT_FILE):
            df.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
            print(f"Appended to {OUTPUT_FILE}")
        else:
            df.to_csv(OUTPUT_FILE, mode="w", header=True, index=False)
            print(f"Created {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
