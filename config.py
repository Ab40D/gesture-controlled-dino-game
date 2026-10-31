"""Central configuration for the Dino hand-gesture controller.

Tweak the values here instead of editing the application logic.
All time values are in seconds, all frame sizes in pixels.
"""

# ------------------------------- Webcam --------------------------------------
CAMERA_INDEX: int = 0        # 0 = default webcam; try 1, 2, ... if you have several
FRAME_WIDTH: int = 1280      # requested capture width  (not all cameras honor it)
FRAME_HEIGHT: int = 720      # requested capture height (not all cameras honor it)

# ---------------------------- MediaPipe Hands --------------------------------
MAX_HANDS: int = 1                 # one hand is enough to play
DETECTION_CONFIDENCE: float = 0.7  # min confidence to accept a NEW hand detection
TRACKING_CONFIDENCE: float = 0.7   # min confidence to keep tracking it frame to frame

# ---------------------------- Gesture logic ----------------------------------
FIST_CONFIRM_FRAMES: int = 3  # CLOSED_FIST must be seen this many frames in a row
#                               before a jump is even considered (anti-flicker)

# ---------------------------- Jump behaviour ---------------------------------
JUMP_COOLDOWN: float = 0.4  # minimum seconds between two jumps (debounce)
STARTUP_DELAY: float = 3.0  # grace period to focus the Dino window; NO key is
#                             sent before this delay has elapsed
