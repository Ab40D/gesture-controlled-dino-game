import cv2
import time

from config import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CAMERA_FPS,
    HAND_DETECTION_CONFIDENCE,
    HAND_TRACKING_CONFIDENCE,
    JUMP_COOLDOWN,
    FIST_CONFIRM_FRAMES,
    STARTUP_DELAY,
)

from gesture_detector import GestureDetector, Gesture
from dino_controller import DinoController


WINDOW_NAME = "Dino Hand Gesture Control"

# Actual display size
DISPLAY_WIDTH = 500
DISPLAY_HEIGHT = 375


WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
YELLOW = (0, 255, 255)
GRAY = (180, 180, 180)


_STATE_TEXT = {
    Gesture.OPEN_PALM: "OPEN PALM",
    Gesture.CLOSED_FIST: "CLOSED FIST",
    Gesture.UNKNOWN: "UNKNOWN",
    Gesture.NO_HAND: "NO HAND",
}


def draw_overlay(
    frame,
    gesture,
    hand_detected,
    jump_count,
    armed,
    fist_streak,
    startup_remaining,
    last_jump_time,
    jump_flash_until,
):
    now = time.monotonic()

    lines = [
        (f"FPS: {fps:.1f}", WHITE),
        (f"HAND: {'YES' if hand_detected else 'NO'}", GREEN if hand_detected else RED),
        (f"GESTURE: {_STATE_TEXT[gesture]}", WHITE),
        (
            "ACTION: JUMP!"
            if now < jump_flash_until
            else f"STATE: {'ARMED' if armed else 'WAITING'}",
            RED if now < jump_flash_until else GREEN,
        ),
        (f"JUMPS: {jump_count}", WHITE),
        (f"FIST FRAMES: {fist_streak}/{FIST_CONFIRM_FRAMES}", WHITE),
    ]

    cooldown_remaining = max(
        0.0,
        JUMP_COOLDOWN - (now - last_jump_time),
    )

    if cooldown_remaining > 0:
        lines.append(
            (f"COOLDOWN: {cooldown_remaining:.1f}s", YELLOW)
        )

    y = 30

    for text, color in lines:
        cv2.putText(
            frame,
            text,
            (15, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
            cv2.LINE_AA,
        )
        y += 28

    if startup_remaining > 0:
        text = f"STARTING... {startup_remaining:.1f}s"

        cv2.putText(
            frame,
            text,
            (15, frame.shape[0] - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            YELLOW,
            2,
            cv2.LINE_AA,
        )

    cv2.putText(
        frame,
        "Q = Quit",
        (frame.shape[1] - 110, frame.shape[0] - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        GRAY,
        1,
        cv2.LINE_AA,
    )


# Global FPS value used by overlay
fps = 0.0


def main():
    global fps

    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("[ERROR] Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

    print("[INFO] Camera started.")

    detector = GestureDetector(
        detection_confidence=HAND_DETECTION_CONFIDENCE,
        tracking_confidence=HAND_TRACKING_CONFIDENCE,
    )

    controller = DinoController(
        cooldown=JUMP_COOLDOWN,
        startup_delay=STARTUP_DELAY,
    )

    # IMPORTANT:
    # AUTOSIZE means the OS window follows the actual image size.
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

    previous_time = time.monotonic()

    jump_count = 0
    fist_streak = 0
    armed = True
    last_jump_time = -999.0
    jump_flash_until = 0.0

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("[ERROR] Could not read camera frame.")
                break

            frame = cv2.flip(frame, 1)

            gesture, hand_detected, landmarks = detector.process(frame)

            if landmarks:
                detector.draw_landmarks(frame, landmarks)

            now = time.monotonic()

            startup_remaining = max(
                0.0,
                controller.start_time + STARTUP_DELAY - now,
            )

            # -----------------------------
            # GESTURE STATE MACHINE
            # -----------------------------

            if gesture == Gesture.CLOSED_FIST:
                fist_streak += 1

                if (
                    fist_streak >= FIST_CONFIRM_FRAMES
                    and armed
                    and startup_remaining <= 0
                    and now - last_jump_time >= JUMP_COOLDOWN
                ):
                    controller.jump()

                    jump_count += 1
                    last_jump_time = now
                    jump_flash_until = now + 0.35

                    armed = False

            elif gesture == Gesture.OPEN_PALM:
                fist_streak = 0
                armed = True

            elif gesture == Gesture.NO_HAND:
                fist_streak = 0
                armed = False

            else:
                fist_streak = 0

            # -----------------------------
            # FPS
            # -----------------------------

            current_time = time.monotonic()
            delta = current_time - previous_time
            previous_time = current_time

            if delta > 0:
                instant_fps = 1.0 / delta
                fps = (fps * 0.9) + (instant_fps * 0.1)

            # -----------------------------
            # DRAW
            # -----------------------------

            draw_overlay(
                frame,
                gesture,
                hand_detected,
                jump_count,
                armed,
                fist_streak,
                startup_remaining,
                last_jump_time,
                jump_flash_until,
            )

            # -----------------------------
            # ONLY RESIZE THE IMAGE
            # -----------------------------

            display_frame = cv2.resize(
                frame,
                (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                interpolation=cv2.INTER_AREA,
            )

            cv2.imshow(WINDOW_NAME, display_frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:
        cap.release()
        detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()