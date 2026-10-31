# 🦖 Dino Hand Gesture Control

Control the **Chrome Dino Game** with your hand: an **open palm** lets the
Dino run, a **closed fist** makes it jump — exactly **once** per fist, never
on repeat. Everything runs **locally and offline**: webcam → OpenCV →
MediaPipe Hands → gesture state machine → PyAutoGUI → `SPACE`.

---

## Table of Contents

1. [Overview](#overview)
2. [Demo Concept](#demo-concept)
3. [Technologies](#technologies)
4. [How the System Works](#how-the-system-works)
5. [Gesture Controls](#gesture-controls)
6. [Requirements](#requirements)
7. [Installation](#installation)
8. [How to Run](#how-to-run)
9. [Configuration](#configuration)
10. [Project Architecture](#project-architecture)
11. [Safety Features](#safety-features)
12. [Troubleshooting](#troubleshooting)
13. [Future Improvements](#future-improvements)
14. [License](#license)

---

## Overview

This project is a small but complete **human-computer interaction** demo built
with classical, landmark-based computer vision — no training, no cloud, no
API keys, no internet connection required for the processing.

* One hand is tracked in real time with **MediaPipe Hands** (21 landmarks).
* A **geometric classifier** decides between `OPEN_PALM`, `CLOSED_FIST`,
  `UNKNOWN` and `NO_HAND` by comparing finger-tip vs. finger-joint distances
  to the wrist for all four long fingers.
* A **state machine** converts the gesture stream into **edge-triggered**
  jump events: a jump fires only on the transition *open palm → closed fist*,
  after the fist has been stable for a few frames and the cooldown has
  elapsed. Holding the fist never re-triggers.
* **PyAutoGUI** sends a single `SPACE` key press to whichever window has
  focus — the Chrome Dino game.

## Demo Concept

The intended demo looks like this (record it with OBS or `peek`, then drop a
`demo.gif` into the repo):

1. The webcam window shows the mirrored camera feed with the hand skeleton
   drawn on top, plus a HUD with FPS, gesture, state, jump count and cooldown.
2. The user shows an open palm → HUD says `GESTURE: OPEN PALM / STATE: NORMAL`,
   the Dino keeps running.
3. The user closes the fist → HUD flashes `ACTION: JUMP!`, one `SPACE` press
   is sent, the Dino jumps once.
4. The fist stays closed → nothing happens. Open palm, fist again → next jump.

## Technologies

| Component            | Library / Tool                                  |
| -------------------- | ----------------------------------------------- |
| Language             | Python 3 (3.9 – 3.12, see note in Requirements) |
| Webcam capture & UI  | OpenCV (`opencv-python`)                        |
| Hand tracking        | MediaPipe Hands (on-device, model bundled)      |
| Keyboard control     | PyAutoGUI                                       |
| Gesture recognition  | Custom geometric classifier (no ML training)    |

## How the System Works

### 1. Frame capture

OpenCV opens the default webcam, requests a 1280×720 stream, mirrors every
frame horizontally (so the feed behaves like a mirror) and displays it in a
window. `Q` quits the program.

### 2. Hand landmark detection

Each frame is converted to RGB and processed by MediaPipe Hands
(`max_num_hands=1`). When a hand is found we get 21 normalized landmarks,
which are converted to pixel coordinates and drawn on top of the frame.

### 3. Gesture classification

For each long finger (index, middle, ring, pinky) the classifier compares two
distances to the wrist:

* fingertip ↔ wrist
* middle joint (PIP) ↔ wrist

An **extended** finger has its tip clearly farther from the wrist than its
PIP joint (with a 10 % margin to reject half-bent poses); a **folded** finger
has it closer. Because the comparison is done per finger and relative to the
wrist, it is robust to hand rotation and to the hand's distance to the camera —
and it never relies on a single landmark distance.

| Extended fingers (of 4) | Gesture       |
| ----------------------- | ------------- |
| 3 or 4                  | `OPEN_PALM`   |
| 0 or 1                  | `CLOSED_FIST` |
| 2                       | `UNKNOWN`     |
| no hand in frame        | `NO_HAND`     |

The thumb is deliberately ignored: its geometry differs from the other
fingers and only adds noise to the palm/fist decision.

### 4. State machine (edge-triggered jumps)

```text
                ┌──────────────┐
                │   NO_HAND    │◀── hand leaves the frame
                └──────────────┘
                       │ hand visible, fingers open
                       ▼
   re-arms      ┌──────────────┐   fist confirmed for FIST_CONFIRM_FRAMES
  ──────────────│  OPEN_PALM   │───────────────┐
   (armed)      └──────────────┘               ▼
                ┌──────────────┐    fires ONE jump, then disarms
                │ CLOSED_FIST  │──── holding the fist → no further jumps
                └──────────────┘
```

* `OPEN_PALM` → state NORMAL, the machine is **armed**, nothing is sent.
* `OPEN_PALM → CLOSED_FIST` (confirmed over a few frames, cooldown elapsed)
  → **exactly one jump**, then the machine is disarmed.
* `CLOSED_FIST` held → no further jumps.
* `NO_HAND` → no jump, and the machine is disarmed (a jump always requires a
  visible open palm first).
* `UNKNOWN` → keeps the current arming state (rides out a single shaky frame).

### 5. Debounce / cooldown

Two independent mechanisms prevent accidental double jumps:

1. **Consistency**: the fist must be classified for `FIST_CONFIRM_FRAMES`
   frames in a row before it counts (default: 3).
2. **Cooldown**: after a jump, at least `JUMP_COOLDOWN` seconds must pass
   before the next one (default: 0.4 s). The HUD shows the remaining time.

### 6. Key press

On a valid jump event the controller calls `pyautogui.press("space")` — a
keyDown immediately followed by a keyUp. The key is **never held down**, so
the Dino performs one normal jump per event. The program never talks to
Chrome directly; the focused window simply receives a real key press.

## Gesture Controls

| Gesture            | Effect on the game                        |
| ------------------ | ----------------------------------------- |
| ✋ Open palm        | NORMAL — the Dino runs, nothing is sent   |
| ✊ Closed fist      | JUMP — one single `SPACE` press           |
| ✊ held closed      | nothing (no auto-repeat)                  |
| 🚫 Hand not visible | nothing (and the machine disarms)         |
| ✋→✊ again          | the next jump                             |

## Requirements

* A webcam and a graphical desktop session.
* Google Chrome with the Dino game (`chrome://dino`, or just disconnect).
* **Python 3.9 – 3.12.** ⚠️ MediaPipe currently does **not** publish wheels
  for Python 3.13. Arch Linux ships the newest Python as its default
  `python` package, so on Arch you will most likely need Python 3.12:

  * **Option A – pyenv** (recommended): `sudo pacman -S pyenv`, then
    `pyenv install 3.12` and use `~/.pyenv/versions/3.12.x/bin/python` below.
  * **Option B – AUR**: `yay -S python312`, then use `python3.12` below.
  * **Option C – uv**: `sudo pacman -S uv`, then
    `uv venv --python 3.12 .venv` and `uv pip install -r requirements.txt`.
* On Linux/X11, PyAutoGUI needs `python-xlib`
  (`sudo pacman -S python-xlib` on Arch).

## Installation

Tested on **Arch Linux**; the same steps work on most distributions.

```bash
# 1. (Arch) system dependencies
sudo pacman -S python-pip git python-xlib
#     ^ plus Python 3.12 via pyenv/AUR/uv if your default python is 3.13+
#       (see "Requirements" above)

# 2. Get the code
git clone <your-repo-url> dino-hand-gesture
cd dino-hand-gesture

# 3. Create and activate a virtual environment
#    (use python3.12 / the pyenv interpreter here if needed)
python -m venv .venv
source .venv/bin/activate

# 4. Install the dependencies
pip install -r requirements.txt
```

> With **uv** the whole flow is just:
> `uv venv --python 3.12 .venv && source .venv/bin/activate && uv pip install -r requirements.txt`

## How to Run

1. Open **Chrome**.
2. Open the **Dino Game**: type `chrome://dino` in the address bar
   (or disconnect from the internet and open any page).
3. Start the program:

   ```bash
   source .venv/bin/activate
   python main.py
   ```

4. A webcam window opens and a countdown is shown:
   **you now have `STARTUP_DELAY` seconds (default 3 s) to click the Dino
   game window** so it has keyboard focus. No key is sent before that.
5. Put an **open palm** in front of the webcam → `GESTURE: OPEN PALM`,
   `STATE: NORMAL` — the Dino runs.
6. **Close your hand into a fist** → the transition is detected, `SPACE` is
   pressed exactly once, the HUD flashes `ACTION: JUMP!` and the Dino jumps.
7. Keep the fist closed → **no** additional jumps.
8. Open the palm again → the machine re-arms.
9. Close the fist again → another jump. 🦖💨
10. Quit with **Q** (camera window focused) or `Ctrl+C` in the terminal.

## Configuration

All tunables live in [`config.py`](config.py) — no need to touch the logic:

| Setting                | Default | Meaning                                            |
| ---------------------- | ------- | -------------------------------------------------- |
| `CAMERA_INDEX`         | `0`     | Which webcam to use (`0`, `1`, …).                 |
| `FRAME_WIDTH`          | `1280`  | Requested capture width.                           |
| `FRAME_HEIGHT`         | `720`   | Requested capture height.                          |
| `MAX_HANDS`            | `1`     | Hands tracked simultaneously.                      |
| `DETECTION_CONFIDENCE` | `0.7`   | Min confidence to accept a new hand.               |
| `TRACKING_CONFIDENCE`  | `0.7`   | Min confidence to keep tracking between frames.    |
| `FIST_CONFIRM_FRAMES`  | `3`     | Consecutive fist frames required before a jump.    |
| `JUMP_COOLDOWN`        | `0.4`   | Minimum seconds between two jumps (debounce).      |
| `STARTUP_DELAY`        | `3.0`   | Seconds before any key press is allowed at start.  |

Tuning tips: jumps feel sluggish → lower `FIST_CONFIRM_FRAMES` to `2`; double
jumps sneak in → raise `JUMP_COOLDOWN` to `0.6`; low FPS → lower
`FRAME_WIDTH`/`FRAME_HEIGHT` to `640`×`480`.

## Project Architecture

```text
dino-hand-gesture/
├── main.py               # event loop, JumpStateMachine, HUD overlay
├── gesture_detector.py   # GestureDetector + geometric gesture classifier
├── dino_controller.py    # DinoController: startup delay + single SPACE press
├── config.py             # all tunable settings
├── requirements.txt      # Python dependencies
├── README.md
└── .gitignore
```

Data flow:

```text
 Webcam
    │
    ▼
 OpenCV ──────────────────── frame capture, mirror, HUD overlay
    │
    ▼
 MediaPipe Hands ─────────── 21 hand landmarks (on-device)
    │
    ▼
 Gesture Recognition ─────── OPEN_PALM / CLOSED_FIST / UNKNOWN / NO_HAND
    │
    ▼
 State Machine ───────────── arms on OPEN PALM, edge-triggers on CLOSED FIST
    │
    ▼
 Jump Event ──────────────── confirm frames + cooldown (debounce)
    │
    ▼
 PyAutoGUI
    │
    ▼
 SPACE
    │
    ▼
 Chrome Dino 🦖
```

## Safety Features

* **Startup delay** (`STARTUP_DELAY`): no keyboard input is possible during
  the first seconds, so you can calmly focus the game window.
* **Edge-trigger only**: the state machine fires on transitions, never while
  a gesture is being held — `SPACE` is never auto-repeated or held down.
* **PyAutoGUI fail-safe**: slamming the mouse into a screen corner aborts the
  program immediately (PyAutoGUI's built-in emergency stop — it is handled
  gracefully by the main loop).
* **No surprises from `NO_HAND`**: losing the hand never fires a jump and
  disarms the machine.

## Troubleshooting

**`pip install mediapipe` fails with "No matching distribution found"**
Your Python is too new (very likely 3.13, the current Arch default).
MediaPipe only ships wheels for Python 3.9–3.12. Use Python 3.12 (see
[Requirements](#requirements)) and recreate the venv with it.

**The webcam doesn't open**
Another application (browser, Zoom, Cheese) is probably holding it. Check
`ls /dev/video*` and try `CAMERA_INDEX = 1` in `config.py` if you have several
cameras. On Linux your user may need to be in the `video` group.

**No jumps happen, although the fist is detected**
Run the checklist: (1) Did the startup countdown finish? (2) Does the Chrome
Dino window have keyboard focus? (3) Was an **open palm** clearly shown
before the fist? (4) Is the cooldown over (HUD says `COOLDOWN: READY`)?
Also try plain `xdotool key space` in a terminal: if that doesn't make the
Dino jump either, the problem is window focus, not this program.

**I'm on Wayland and key presses don't reach Chrome**
PyAutoGUI only talks to X11. Log out and choose an **Xorg/X11 session** at
the login screen, or run Chrome under XWayland. The webcam preview itself
works fine on Wayland — only the synthetic key presses don't.

**`ImportError: libGL.so.1` when importing cv2**
Install the OpenGL runtime libraries: `sudo pacman -S libglvnd mesa` (Arch).

**`cv2.imshow` crashes with GTK/Qt errors on a minimal system**
The OpenCV GUI needs a widget toolkit: `sudo pacman -S gtk3 qt6-base`.

**`AttributeError: module 'mediapipe' has no attribute 'solutions'`**
Your MediaPipe installation is broken or shadowed by another package/file
named `mediapipe`. Reinstall inside a clean venv:
`pip install --force-reinstall mediapipe`.

**MediaPipe pulled in `opencv-contrib-python` as well**
That's normal — MediaPipe declares it as a dependency. It provides the same
`cv2` module and coexists with `opencv-python` fine.

**Gestures flicker between OPEN PALM and UNKNOWN**
Improve the lighting, keep the hand fully inside the frame and roughly facing
the camera. If needed, raise `DETECTION_CONFIDENCE`.

**FPS is low**
Lower the resolution in `config.py` (e.g. 640×480) and close other
camera/GPU-heavy applications.

## Future Improvements

* **Duck gesture** — e.g. a quick downward hand swipe maps to `ARROW DOWN`.
* **Two-hand mode** — left fist = jump, right fist = duck.
* **Calibration screen** — capture open/fist reference poses at startup and
  adapt the thresholds to the user's hand.
* **Sensitivity presets** — `config.py` profiles for small hands / far away /
  low light.
* **Unit tests** — synthetic-landmark tests for the classifier and the state
  machine.
* **Alternative tracker** — port to the newer MediaPipe Tasks API
  (`HandLandmarker`) for extra speed.
* **Pause/resume hotkey** — toggle keyboard control without quitting.

## License

MIT — do whatever you like, but have fun jumping over cacti. 🌵
