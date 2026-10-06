# 🏋️‍♂️ GymMentor AI — Real-Time AI Fitness Coach

<div align="center">

# 🏋️‍♂️ Gym Mentor AI — Real-Time AI Fitness Coach

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-00B2FF?style=for-the-badge&logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Headless-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM%20Coaching-F55036?style=for-the-badge&logo=ai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<br/>

**Turns your webcam into a real-time personal trainer: pose tracking, rep counting, form scoring and spoken AI coaching.**

[🚀 Try it Live](https://gym-mentor-ai-jeevan-main.streamlit.app/) · [🌐 Landing Page](https://ariesjeev-gym-mentor-ai-frontend.vercel.app/) · [Report Bug](https://github.com/Ariesjeev/gym-mentor-ai-Jeevan-main/issues)

</div>

---

## 📑 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Exercise Library](#-exercise-library)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup Locally](#%EF%B8%8F-setup-locally)
- [Problems I Faced](#-problems-i-faced)
- [Known Limitations](#-known-limitations)
- [Roadmap](#-roadmap)

---

## 🌟 Overview

Most fitness apps only log sets and reps — they can't tell you your squat depth was shallow or your back rounded on rep 7. **Gym Mentor AI** watches you through your webcam, using **Google MediaPipe** pose estimation and vector-angle math to track joint positions in real time, then uses **Groq's Llama 3** to turn those raw signals into short, spoken coaching cues — delivered as you train, not after.

## ✨ Features

- 🦾 **Real-time pose tracking** — MediaPipe landmarks streamed live over the browser via `streamlit-webrtc`
- 🔢 **Automatic rep & set counting** — a state machine per exercise avoids false positives from camera jitter
- 📐 **Joint-angle form scoring** — vector math on key joints (knee, elbow, hip, shoulder) checks depth and alignment
- 🗣️ **AI voice coaching** — Groq (`llama-3.3-70b-versatile`) generates short corrective/encouraging cues, spoken with gTTS (pyttsx3 as fallback)
- 🗂️ **Workout history** — sessions are logged to SQLite under a simple username login
- 🎨 **Clean Streamlit UI** — live video panel with rep count, set progress and coach feedback

## 🎯 Exercise Library

| Exercise | Tracked Angles | What the coach checks |
|---|---|---|
| 🏋️ **Squats** | Knee, hip, back line | Depth and torso lean |
| 🤸 **Push-ups** | Elbow, body line | Range of motion, sagging hips |
| 💪 **Biceps Curls** | Elbow flexion | Full range, elbow drift |
| 🏋️‍♀️ **Shoulder Press** | Shoulder elevation, elbow lock | Overhead lockout, symmetry |
| 🦵 **Lunges** | Front knee, rear hinge | Knee-over-toe, balance |

## 🔄 How It Works

![Processing Pipeline](./gym-mentor-architecture.png)

1. **Camera** — your browser streams webcam video locally via WebRTC; nothing is uploaded.
2. **MediaPipe** — extracts body landmarks frame by frame.
3. **Exercise Logic** (`core/`, `detectors/`) — computes joint angles and runs each exercise's rep/form state machine.
4. **AI Coach** (`services/`) — sends form events to Groq's Llama 3 model for a short coaching message.
5. **Voice** — the message is spoken aloud with gTTS, so you can keep training without watching the screen.
6. **History** — each session is saved to SQLite against your username.

## 🧰 Tech Stack

| Category | Tools |
|---|---|
| App framework | `streamlit`, `streamlit-webrtc` |
| Computer vision | `mediapipe`, `opencv-python-headless` |
| AI coaching | `groq` (Llama 3) |
| Voice | `gTTS`, `pyttsx3` |
| Data | `numpy`, `pandas`, SQLite |
| Config | `python-dotenv` |

## 📁 Project Structure

```
gym-mentor-ai-Jeevan-main/
├── main.py              # Streamlit entry point
├── requirements.txt
├── packages.txt          # system libs for OpenCV/MediaPipe (libgl1, libglib2.0-0)
├── core/                 # Base exercise interface / shared pose math
├── detectors/            # One detector per exercise (squat, pushup, curl, press, lunge)
├── services/              # AI coaching (Groq), voice (gTTS/pyttsx3), auth, history
└── static/               # CSS / UI assets
```

## ⚙️ Setup Locally

```bash
git clone https://github.com/Ariesjeev/gym-mentor-ai-Jeevan-main.git
cd gym-mentor-ai-Jeevan-main

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

> On Linux/Streamlit Cloud, also install the system packages listed in `packages.txt` (`libgl1`, `libglib2.0-0`) so OpenCV and MediaPipe can load.

Add your Groq key in `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```

Run it:

```bash
streamlit run main.py
```

Open `http://localhost:8501`, allow camera access, log in with a username, pick an exercise and start your set.

## 😓 Problems I Faced

<!-- Replace with your own real challenges — interviewers ask about these. -->
- **Problem:** AI voice coaching wasn't playing at the start of a workout or mid-exercise. **Solution:** _[add what fixed it — e.g. caching audio, triggering playback on a user gesture, switching between gTTS and pyttsx3]_
- **Problem:** `mediapipe`/`opencv` failing to load on deployment. **Solution:** Added `packages.txt` with `libgl1` and `libglib2.0-0` so the headless OpenCV build has its system dependencies on Streamlit Cloud.
- **Problem:** _[add another real one, e.g. rep counting false positives from camera jitter]_. **Solution:** _[how you solved it]_

## ⚠️ Known Limitations

- Accuracy depends on camera angle, lighting and how much of your body is in frame
- Voice coaching latency depends on the Groq API response time
- No login security beyond a username (no password) — fine for a demo, not for production

## 🚀 Roadmap

- [ ] Add more exercises (deadlifts, planks)
- [ ] Mobile-friendly camera layout
- [ ] Per-exercise progress charts from workout history

## 👤 Author

**Jeevan Bikash Sahoo** — Full Stack Developer & AI Engineer
[GitHub](https://github.com/Ariesjeev) · [LinkedIn](https://www.linkedin.com/in/jeevan02/) · [Twitter/X](https://x.com/jeevan_bikash)

---

<div align="center">⭐ If you found this useful, consider giving it a star</div>
