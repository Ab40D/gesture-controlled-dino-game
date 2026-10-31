"""Hand detection and gesture classification built on MediaPipe Hands.

The classifier is purely geometric - no machine learning on our side.  For
every long finger (index, middle, ring, pinky) it compares the distance from
its TIP to the wrist with the distance from its middle joint (PIP) to the
wrist:

* extended finger -> the tip is clearly *farther* from the wrist than the PIP
* folded finger   -> the tip is *closer* to the wrist than the PIP

Using all four fingers (instead of a single landmark distance) makes the
decision stable, and comparing distances to the wrist makes it independent of
hand orientation and of the hand's distance to the camera.
"""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import cv2
import mediapipe as mp
import numpy as np

import config


class Gesture(enum.Enum):
    """The high-level gestures understood by the game controller."""

    OPEN_PALM = "OPEN PALM"
    CLOSED_FIST = "CLOSED FIST"
    UNKNOWN = "UNKNOWN"      # hand visible, but posture is ambiguous
    NO_HAND = "NO HAND"      # no hand in the frame


@dataclass
class Detection:
    """Result of analysing a single webcam frame."""

    gesture: Gesture
    hand_detected: bool
    # MediaPipe NormalizedLandmarkList, kept around so the UI can draw it.
    landmarks: Optional[object] = None


class GestureDetector:
    """Detects one hand per frame and classifies its posture."""

    # MediaPipe hand-landmark indices.
    WRIST = 0
    # (TIP, PIP) landmark pairs: index, middle, ring and pinky finger.
    FINGERS: Tuple[Tuple[int, int], ...] = ((8, 6), (12, 10), (16, 14), (20, 18))

    # A finger only counts as extended when its tip is at least 10 % farther
    # from the wrist than its PIP joint.  The margin filters out "half bent"
    # poses that would otherwise flicker between palm and fist.
    _EXTEND_MARGIN: float = 1.10

    def __init__(
        self,
        max_hands: int = config.MAX_HANDS,
        detection_confidence: float = config.DETECTION_CONFIDENCE,
        tracking_confidence: float = config.TRACKING_CONFIDENCE,
    ) -> None:
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,  # video stream: reuse tracking between frames
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self._drawing = mp.solutions.drawing_utils
        self._drawing_styles = mp.solutions.drawing_styles
        self._connections = mp.solutions.hands.HAND_CONNECTIONS

    # ------------------------------------------------------------------- API
    def detect(self, frame_bgr: np.ndarray) -> Detection:
        """Analyse one BGR frame and return the current hand posture."""
        # MediaPipe expects RGB images.
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False  # performance hint (avoids an internal copy)
        results = self._hands.process(rgb)

        if not results.multi_hand_landmarks:
            return Detection(gesture=Gesture.NO_HAND, hand_detected=False)

        hand_landmarks = results.multi_hand_landmarks[0]
        height, width = frame_bgr.shape[:2]
        points = self._to_pixels(hand_landmarks, width, height)
        gesture = self.classify(points)
        return Detection(
            gesture=gesture, hand_detected=True, landmarks=hand_landmarks
        )

    def draw_landmarks(self, frame_bgr: np.ndarray, landmarks: object) -> None:
        """Overlay the 21 landmarks and their connections on the frame."""
        self._drawing.draw_landmarks(
            frame_bgr,
            landmarks,
            self._connections,
            self._drawing_styles.get_default_hand_landmarks_style(),
            self._drawing_styles.get_default_hand_connections_style(),
        )

    def close(self) -> None:
        """Release MediaPipe resources."""
        self._hands.close()

    # -------------------------------------------------------------- internals
    @staticmethod
    def _to_pixels(
        hand_landmarks: object, width: int, height: int
    ) -> list[tuple[float, float]]:
        """Convert normalized landmarks to pixel coordinates.

        Working in pixels keeps the distance maths correct even when the
        frame is not square (normalized x and y would otherwise be stretched
        by different factors).
        """
        return [
            (lm.x * width, lm.y * height) for lm in hand_landmarks.landmark
        ]

    @classmethod
    def classify(cls, points: Sequence[Tuple[float, float]]) -> Gesture:
        """Classify a hand from its 21 landmark coordinates (pixel space).

        * >= 3 extended long fingers -> OPEN_PALM
        * <= 1 extended long finger  -> CLOSED_FIST
        * anything in between        -> UNKNOWN

        The thumb is ignored on purpose: its geometry differs from the other
        fingers and adds noise without helping the palm/fist decision.
        """
        wrist = points[cls.WRIST]
        extended = sum(
            1
            for tip_idx, pip_idx in cls.FINGERS
            if cls._finger_is_extended(points, wrist, tip_idx, pip_idx)
        )

        if extended >= 3:
            return Gesture.OPEN_PALM
        if extended <= 1:
            return Gesture.CLOSED_FIST
        return Gesture.UNKNOWN

    @classmethod
    def _finger_is_extended(
        cls,
        points: Sequence[Tuple[float, float]],
        wrist: Tuple[float, float],
        tip_idx: int,
        pip_idx: int,
    ) -> bool:
        """True when the fingertip is clearly farther from the wrist than PIP."""
        tip_dist = math.dist(points[tip_idx], wrist)
        pip_dist = math.dist(points[pip_idx], wrist)
        return tip_dist > pip_dist * cls._EXTEND_MARGIN
