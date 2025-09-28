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

def send_to_encoders(word_count, wpm, audio_file):
    text_encoder = TextEncoder()
    print("Reading transcripts...")
    text_grades, context, examples = text_encoder.encode_and_contextualize("preprocessing/transcript.txt", word_count, wpm, "can_take_input_from_user")
    print("Extracting text features...")
    print(text_grades)
    print(context)
    print(examples)
    

    audio_encoder = AudioEncoder(text_grades, context, audio_file)
    audio_grades = audio_encoder.encode_and_contextualize()
    print("Context ", context)  
    print("Getting Audio grades ", audio_grades)
    print("Sent to encoders successfully.")

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

    audio_16k = librosa.resample(data, orig_sr=samplerate, target_sr=16000)
    audio_16k = audio_16k.astype(np.float32)
    audio_16k = whisper.pad_or_trim(audio_16k)

    mel = whisper.log_mel_spectrogram(audio_16k)

    # --- Load Whisper model & transcribe ---
    print("Loading Whisper model...")
    model = whisper.load_model(model_size)
    mel = mel.to(model.device)

    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    transcript = result.text

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

    send_to_encoders(word_count, wpm, audio_file)
    return str(output_file)
