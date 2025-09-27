import subprocess
import os
import sys
import whisper
import ffmpeg

from models.audio_encoder import AudioEncoder
from models.video_encoder import VideoEncoder
from models.text_encoder import TextEncoder
from models.multimodal_coach import Coach

# Initialize encoders and coach
audio_encoder = AudioEncoder()
video_encoder = VideoEncoder()
text_encoder = TextEncoder()
coach = Coach()

# Load Whisper model once
whisper_model = whisper.load_model("base")

def convert_video_to_audio(video_file, output_ext="mp3"):
    filename, _ = os.path.splitext(video_file)
    audio_path = f"{filename}.{output_ext}"
    print(f"Converting video to audio: {video_file} -> {audio_path}")
    subprocess.call(
        ["ffmpeg", "-y", "-i", video_file, audio_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return audio_path

def transcribe_audio(audio_file):
    print(f"Transcribing audio: {audio_file}")
    result = whisper_model.transcribe(audio_file)
    return result["text"]

def get_audio_duration(file_path):
    print(f"Getting audio duration for: {file_path}")
    probe = ffmpeg.probe(file_path)
    return float(probe['format']['duration'])

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]

    # Step 0: Get speech purpose from user
    speech_purpose = input("What is the purpose of this speech (e.g., 'class presentation', 'argumentative speech', 'job interview', 'storytelling')? ")

    # Step 1: convert video → audio (still needed for Whisper)
    audio_file = convert_video_to_audio(video_file)
    print(f"Audio saved to {audio_file}")

    # Step 2: transcribe audio → text
    transcript_text = transcribe_audio(audio_file)
    transcript_file = f"{os.path.splitext(video_file)[0]}_transcript.txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    print(f"Transcript saved to {transcript_file}")

    # Step 3: get audio duration
    duration = get_audio_duration(audio_file)
    print(f"Video duration: {duration:.2f}s")

    # Step 4: TextEncoder performs context extraction, example retrieval, and rubric grading
    print("Extracting speech context and finding public speaking examples...")
    text_features, context_info, examples_info = text_encoder.encode_and_contextualize(
        transcript_file, duration, speech_purpose
    )
    print("Text features (rubric scores) obtained.")
    print(f"Speech Context: {context_info}")
    print(f"Public Speaking Examples: {examples_info}")

    # Step 5: Coach analyzes performance using video, audio, text features, context, and examples
    print("Analyzing performance using multimodal coach...")
    feedback = coach.analyze_performance(
        video_file, audio_file, text_features, context_info, examples_info
    )
    print("\n--- Coach Feedback ---")
    print(feedback)

    # Optional: Clean up generated audio and transcript files
    # os.remove(audio_file)
    # os.remove(transcript_file)

if __name__ == "__main__":
    main()