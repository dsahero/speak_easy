# ==============================
# main.py
# ==============================

import sys
from preprocessing.process_video import process_video

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <video_file>")
        sys.exit(1)

    input_video = sys.argv[1]
    transcript_file = process_video(input_video, model_size="base")

    print(f"\n✅ Done! Transcript available at: {transcript_file}")

if __name__ == "__main__":
    main()
