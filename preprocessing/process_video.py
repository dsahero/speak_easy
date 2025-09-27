# ==============================
# process_video.py
# ==============================

import re
import whisper
import soundfile as sf
import numpy as np
from pathlib import Path
from moviepy import VideoFileClip
import librosa

from models.text_encoder import TextEncoder
from models.audio_encoder import AudioEncoder
from models.multimodal_coach import Coach

def send_to_encoders():
    text_encoder = TextEncoder()
    print("Reading transcripts...")
    text_encoder.read_transcript("preprocessing/transcript.txt")
    print("Extracting text features...")
    context = text_encoder.extract_context("public speaking")
    grades = text_encoder

    print("Extracting audio features...")
    audio_encoder = AudioEncoder()
    audio_context = audio_encoder.extract_context(context)
    print("Grades:", grades)
    print("Audio Context:", audio_context)  
    print("Sent to encoders successfully.")

    # coach = Coach()
    # coach.analyze_performance(
    #     text_features=grades,
    #     context=audio_context,
    #     examples_info=""
    # )

def process_video(input_video: str, model_size: str = "base") -> str:
    """
    Process a video file: extract audio, transcribe with Whisper,
    analyze speech, and save transcript to preprocessing/transcript.txt

    Args:
        input_video (str): Path to the input video file (e.g., .mp4)
        model_size (str): Whisper model size ("tiny", "base", "small", etc.)

    Returns:
        str: Path to the saved transcript file
    """
    audio_file = Path(input_video).with_suffix(".wav")

    # --- Extract audio ---
    print(f"Extracting audio from {input_video} ...")
    audio_clip = VideoFileClip(input_video).audio
    audio_clip.write_audiofile(audio_file, logger=None)
    audio_clip.close()
    print(f"Audio saved to {audio_file}")

    if not Path(audio_file).exists():
        raise FileNotFoundError(f"File not found: {audio_file}")

    # --- Load audio & preprocess for Whisper ---
    data, samplerate = sf.read(audio_file)
    if len(data.shape) > 1:
        data = data.mean(axis=1)  # convert to mono

    print("Loading Whisper model...")
    model = whisper.load_model(model_size)

    print(f"Transcribing {audio_file} ...")
    result = model.transcribe(str(audio_file))
    transcript = result["text"]


    print("\n📝 Transcript:\n", transcript)

    # --- Save transcript ---
    output_file = Path(__file__).parent / "transcript.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"\n💾 Transcript saved to {output_file}")

    # --- Analyze speech ---
    fillers = ["um", "uh", "like", "you know", "so"]
    filler_counts = {
        f: len(re.findall(rf"\b{f}\b", transcript, flags=re.IGNORECASE))
        for f in fillers
    }

    print("\n⚠️ Filler Word Counts:")
    for f, count in filler_counts.items():
        print(f"{f}: {count}")

    duration_sec = len(data) / samplerate
    word_count = len(transcript.split())
    wpm = word_count / (duration_sec / 60)
    print(f"\n⏱️ Speaking Speed: {wpm:.2f} words per minute")

    send_to_encoders(duration_sec, word_count, wpm, filler_counts)
    return str(output_file)
