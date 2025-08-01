import os
import hashlib
from datetime import datetime

try:
    import cv2
except Exception:
    cv2 = None  # type: ignore


def capture_frame(device: int = 0) -> tuple[str, str | None]:
    """Capture a frame from the webcam and return a token and image path."""
    if cv2 is None:
        print("[Video] opencv-python not installed; skipping webcam capture")
        return "", None

    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print("[Video] Unable to open webcam")
        return "", None

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("[Video] Failed to capture frame")
        return "", None

    os.makedirs("modalities/webcam", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join("modalities/webcam", f"frame_{ts}.png")
    try:
        cv2.imwrite(image_path, frame)
    except Exception as e:
        print(f"[Video] Error saving frame: {e}")
        return "", None

    token = hashlib.sha1(frame.tobytes()).hexdigest()[:8]
    return token, image_path
