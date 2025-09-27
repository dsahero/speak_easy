# SpeakEasy Backend API

Flask-based backend API for the SpeakEasy AI speech analysis platform.

## Features

- 🎥 **Video Processing**: Handles video upload and conversion
- 🎤 **Audio Transcription**: Uses OpenAI Whisper for speech-to-text
- 🤖 **AI Analysis**: Integrates with Google Gemini for context analysis
- 📊 **Scoring System**: Comprehensive speech performance metrics
- 🎯 **Coach Feedback**: AI-powered coaching recommendations

## Setup

### Prerequisites

- Python 3.10+
- FFmpeg installed on system
- Google Gemini API key

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

5. Run the Flask app:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### POST /api/analyze

Analyzes a speech video and returns comprehensive feedback.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `video`: Video file (MP4, AVI, MOV, etc.)
  - `speech_purpose`: Purpose of the speech (optional)

**Response:**
```json
{
  "overall_score": 0.85,
  "transcript_scores": {
    "content_quality": {
      "clarity_score": 0.82,
      "relevance_score": 0.91,
      "example_usage_score": 0.74
    },
    "structure": {
      "logical_flow_score": 0.79,
      "transition_score": 0.68,
      "balance_score": 0.83
    },
    "vocabulary_style": {
      "lexical_richness": 0.72,
      "word_appropriateness": 0.80,
      "repetition_score": 0.65
    },
    "grammar_fluency": {
      "grammar_correctness": 0.89,
      "sentence_fluency": 0.77,
      "filler_word_density": 0.88
    },
    "speaking_length": {
      "word_count": 120,
      "words_per_minute": 12,
      "length_score": 0.1
    },
    "video_duration_seconds": 600.0
  },
  "speech_context": {
    "specific_topic": "bioluminescence in squid",
    "general_topic": "marine biology",
    "format": "scientific academic paper conference"
  },
  "coach_feedback": "Great job! Your speech was well-structured...",
  "public_speaking_examples": "Example 1: TED Talk on deep-sea creatures...",
  "analysis_timestamp": "2024-01-15T10:30:00"
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Architecture

The backend follows this processing pipeline:

1. **Video Upload**: Receives video file via multipart form
2. **Audio Extraction**: Converts video to audio using FFmpeg
3. **Speech Transcription**: Uses OpenAI Whisper for speech-to-text
4. **Context Analysis**: Uses Google Gemini to extract speech context
5. **Scoring**: Analyzes transcript for various performance metrics
6. **Coach Feedback**: Generates personalized coaching recommendations
7. **Response**: Returns comprehensive analysis results

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **OpenAI Whisper**: Speech recognition
- **Google Gemini**: AI analysis and feedback
- **FFmpeg**: Video/audio processing
- **PyTorch**: Machine learning framework

## Error Handling

The API includes comprehensive error handling:

- File validation (video format, size limits)
- Processing errors (transcription failures)
- API errors (Gemini API issues)
- Cleanup (temporary file removal)

## Development

To run in development mode:

```bash
export FLASK_ENV=development
python app.py
```

## Production Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn)
2. Set up proper environment variables
3. Configure reverse proxy (Nginx)
4. Set up monitoring and logging

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Security Considerations

- File upload validation
- Temporary file cleanup
- API key security
- CORS configuration
- Input sanitization

## Monitoring

The API includes health checks and error logging for monitoring:

- Health endpoint for uptime monitoring
- Error responses with detailed messages
- Processing time tracking
- File cleanup verification
