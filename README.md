# 🦖 Gesture-Controlled Dino Game

### Play the Chrome Dino Game using nothing but your hands.

<p align="center">
  <img src="assets/dino-running.gif" width="300" alt="Animated running dinosaur" />
</p>

<p align="center">
  <b>Real-time Hand Tracking · Computer Vision · Gesture Recognition</b>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=gwzYbDqNV2c">
    <img src="https://img.shields.io/badge/▶_Watch_Demo-YouTube-red?style=for-the-badge&logo=youtube" alt="Watch Demo"/>
  </a>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
  <img src="https://img.shields.io/badge/MediaPipe-Hand_Tracking-0097A7?style=for-the-badge"/>
</p>

---

## 🎮 About the Project

What if you could play the Chrome Dinosaur Game without touching your keyboard?

**Gesture-Controlled Dino Game** is a Python-based computer vision project that transforms real-time hand gestures into game controls.

Using a webcam, the system detects and interprets hand movements, then translates them into keyboard actions to control the iconic Chrome Dino.

No physical controller. No keyboard interaction. Just your hand.

## ✨ Key Features

| Feature | Description |
|---|---|
| 🖐️ Real-time Hand Tracking | Detects hand landmarks through your webcam. |
| ✋ Open Palm | Keeps the game running. |
| ✊ Closed Fist | Triggers a single jump. |
| ⚡ Gesture Debouncing | Prevents repeated jump inputs while holding a fist. |
| 🎥 Live Camera Processing | Processes webcam frames in real time. |
| 🎮 Automated Game Control | Sends keyboard actions through PyAutoGUI. |

## 🧠 How It Works

The system connects computer vision with human-computer interaction.

```text
       WEBCAM
          |
          v
    OPENCV PROCESSING
          |
          v
   MEDIAPIPE HAND TRACKING
          |
          v
    GESTURE RECOGNITION
          |
          v
     ACTION MAPPING
          |
          v
       PYAUTOGUI
          |
          v
    CHROME DINO GAME
```

### Gesture Mapping

| Hand Gesture | Game Action |
|---|---|
| Open Palm 🖐️ | Neutral / Running |
| Closed Fist ✊ | Jump |

The gesture detection logic includes input control to avoid triggering multiple jumps from a single held gesture.

## 🛠️ Tech Stack

- **Python** — Core implementation.
- **OpenCV** — Real-time video capture and image processing.
- **MediaPipe** — Hand landmark detection and tracking.
- **PyAutoGUI** — Keyboard automation and game interaction.

## 📂 Project Structure

```text
gesture-controlled-dino-game/
│
├── main.py
├── config.py
├── gesture_detector.py
├── dino_controller.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── assets/
    └── dino-running.gif
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Ab40D/gesture-controlled-dino-game.git
cd gesture-controlled-dino-game
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the project

Open the Chrome Dino Game, make sure your webcam is available, then execute:

```bash
python main.py
```

Follow the on-screen instructions if provided by the application.

## 📹 Project Demonstration

Watch the controller in action:

<p align="center">
  <a href="https://www.youtube.com/watch?v=gwzYbDqNV2c">
    <img src="https://img.youtube.com/vi/gwzYbDqNV2c/maxresdefault.jpg" width="85%" alt="Gesture Controlled Dino Game Demo"/>
  </a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=gwzYbDqNV2c">
    ▶ Watch the Full Demonstration
  </a>
</p>

## 🔬 Development & Future Improvements

The core implementation is functional. Future development will explore:

- More advanced gesture recognition.
- Improved detection under different lighting conditions.
- Additional hand gestures for different game actions.
- Reduced processing latency.
- Enhanced visual feedback and user experience.

## 🎯 Developer's Note

The controller works — my Dino skills, however, still need some work haha.

This project is part of my ongoing exploration of computer vision, real-time automation, and alternative human-computer interaction methods.

Building technology that makes interaction more natural, accessible, and intuitive.

---

## 👨‍💻 About the Developer

**Abdelkhalek Mammeri**

Engineer & Electronics Student | Systems Integration · Automation · IoT · Computer Vision

I enjoy building practical systems that connect software, electronics, automation, and the physical world.

### Connect with me

<p align="left">
  <a href="https://github.com/Ab40D">
    <img src="https://img.shields.io/badge/GitHub-Ab40D-181717?style=for-the-badge&logo=github" alt="GitHub"/>
  </a>
  <a href="https://www.linkedin.com/in/abdelkhalekmammeri/">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin" alt="LinkedIn"/>
  </a>
  <a href="https://se7en-bay.vercel.app/">
    <img src="https://img.shields.io/badge/Portfolio-Visit-000000?style=for-the-badge&logo=vercel" alt="Portfolio"/>
  </a>
  <a href="https://www.youtube.com/watch?v=gwzYbDqNV2c">
    <img src="https://img.shields.io/badge/YouTube-Demo-FF0000?style=for-the-badge&logo=youtube" alt="YouTube"/>
  </a>
</p>

---

<p align="center">
  <b>Built with Python, Computer Vision, and a little bit of Dino chaos. 🦖</b>
</p>
