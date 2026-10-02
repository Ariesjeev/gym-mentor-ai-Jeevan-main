import time
import streamlit as st

from services.coaching.voice_pipeline import VoicePipeline


class DummyTTS:
    def text_to_speech(self, text, gender="Female", volume=1.0):
        time.sleep(0.6)
        return b"audio-bytes"


def test_voice_pipeline_speak_is_non_blocking():
    st.session_state.clear()
    st.session_state.voice_enabled = True
    st.session_state.voice_volume = 1.0
    st.session_state.voice_gender = "Female"
    st.session_state.voice_engine = "pyttsx3 / gTTS"

    pipeline = VoicePipeline(llm=None, tts=DummyTTS())
    start = time.perf_counter()
    result = pipeline.speak("Fix your knees.", priority="normal")
    elapsed = time.perf_counter() - start

    assert elapsed < 0.35, f"speak blocked for {elapsed:.2f}s"
    assert result is None


def test_web_speech_is_forwarded_to_browser_queue():
    st.session_state.clear()
    st.session_state.voice_enabled = True
    st.session_state.voice_volume = 1.0
    st.session_state.voice_gender = "Female"
    st.session_state.voice_engine = "Web Speech API"

    pipeline = VoicePipeline(llm=None, tts=None)
    pipeline.speak("Fix your knees.", priority="normal")

    speech_item = pipeline.pending_browser_speech.get(timeout=1.0)
    assert speech_item["text"] == "Fix your knees."
    assert speech_item["priority"] == "normal"
