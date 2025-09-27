from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import json
from datetime import datetime
import tempfile

# Import your existing modules
import sys
sys.path.append('..')
from models.audio_encoder import AudioEncoder
from models.video_encoder import VideoEncoder
from models.text_encoder import TextEncoder
from models.multimodal_coach import Coach

app = Flask(__name__)
CORS(app)

# Initialize encoders and coach
audio_encoder = AudioEncoder()
video_encoder = VideoEncoder()
text_encoder = TextEncoder()
coach = Coach()

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        speech_purpose = request.form.get('speech_purpose', 'general presentation')
        
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            video_file.save(temp_video.name)
            video_path = temp_video.name
        
        try:
            # Step 1: Convert video to audio
            audio_path = convert_video_to_audio(video_path)
            
            # Step 2: Transcribe audio
            transcript_text = transcribe_audio(audio_path)
            transcript_file = f"{os.path.splitext(video_path)[0]}_transcript.txt"
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            
            # Step 3: Get audio duration
            duration = get_audio_duration(audio_path)
            
            # Step 4: Text analysis and context extraction
            text_features, context_info, examples_info = text_encoder.encode_and_contextualize(
                transcript_file, duration, speech_purpose
            )
            
            # Step 5: Coach analysis
            feedback = coach.analyze_performance(
                video_path, audio_path, text_features, context_info, examples_info
            )
            
            # Calculate overall score
            overall_score = calculate_overall_score(text_features)
            
            # Prepare response
            response_data = {
                'overall_score': overall_score,
                'transcript_scores': text_features,
                'speech_context': context_info,
                'coach_feedback': feedback,
                'public_speaking_examples': examples_info,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return jsonify(response_data)
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(video_path)
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                if os.path.exists(transcript_file):
                    os.unlink(transcript_file)
            except:
                pass
                
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

def convert_video_to_audio(video_file, output_ext="mp3"):
    """Convert video to audio using ffmpeg"""
    filename, _ = os.path.splitext(video_file)
    audio_path = f"{filename}.{output_ext}"
    
    subprocess.call(
        ["ffmpeg", "-y", "-i", video_file, audio_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return audio_path

def transcribe_audio(audio_file):
    """Transcribe audio using Whisper"""
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]

def get_audio_duration(file_path):
    """Get audio duration using ffmpeg"""
    import ffmpeg
    probe = ffmpeg.probe(file_path)
    return float(probe['format']['duration'])

def calculate_overall_score(text_features):
    """Calculate overall score from individual metrics"""
    if not text_features:
        return 0.0
    
    scores = []
    
    # Extract scores from different categories
    for category, metrics in text_features.items():
        if isinstance(metrics, dict):
            for metric, value in metrics.items():
                if isinstance(value, (int, float)) and 0 <= value <= 1:
                    scores.append(value)
    
    return sum(scores) / len(scores) if scores else 0.0

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
