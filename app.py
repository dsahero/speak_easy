# ==============================
# app.py (Flask backend)
# ==============================

from flask import Flask, request, jsonify
from preprocessing.process_video import process_video
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from flask import send_from_directory

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists("frontend/build/" + path):
        return send_from_directory("frontend/build", path)
    else:
        return send_from_directory("frontend/build", "index.html")

@app.route("/process", methods=["POST"])
def process():
    """
    Accepts a video file (multipart/form-data) or file path (JSON),
    processes it, and returns metrics + transcript path.
    """
    # Case 1: file upload
    if "file" in request.files:
        video = request.files["file"]
        save_path = os.path.join("uploads", video.filename)
        os.makedirs("uploads", exist_ok=True)
        video.save(save_path)
        input_video = save_path
    else:
        # Case 2: JSON body with file path
        data = request.get_json()
        if not data or "file_path" not in data:
            return jsonify({"error": "No video file provided"}), 400
        input_video = data["file_path"]

    # Updated to unpack everything
    audio_grades, text_grades, context, examples = process_video(save_path, model_size="base")

    return jsonify({
        "message": "Processing complete ✅",
        "results": {
            "audio_grades": audio_grades,
            "text_grades": text_grades,
            "context": context,
            "examples": examples
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)



# # ==============================
# # main.py
# # ==============================

# import sys
# from preprocessing.process_video import process_video

# def main():
#     if len(sys.argv) < 2:
#         print("Usage: python main.py <video_file>")
#         sys.exit(1)

#     input_video = sys.argv[1]
#     transcript_file = process_video(input_video, model_size="base")

#     print(f"\n✅ Done! Transcript available at: {transcript_file}")

# if __name__ == "__main__":
#     main()
