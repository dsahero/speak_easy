# 🎤 SpeakEasy - AI Speech Analysis Platform

A comprehensive AI-powered platform for analyzing and improving public speaking skills. Upload your speech videos and receive detailed feedback, scoring, and personalized coaching recommendations.

## ✨ Features

- 🎥 **Video Upload**: Drag & drop video upload with progress tracking
- 🎤 **Speech Transcription**: Automatic speech-to-text using OpenAI Whisper
- 🤖 **AI Analysis**: Context-aware analysis using Google Gemini
- 📊 **Detailed Scoring**: Comprehensive metrics across multiple dimensions
- 🎯 **Personalized Coaching**: AI-generated feedback and recommendations
- 📱 **Responsive Design**: Modern UI that works on all devices
- 🚀 **Real-time Processing**: Live progress updates during analysis

## 🏗️ Architecture

```
speak_easy/
├── models/                 # AI model implementations
│   ├── audio_encoder.py   # Audio feature extraction
│   ├── video_encoder.py    # Video feature extraction
│   ├── text_encoder.py     # Text analysis and context extraction
│   └── multimodal_coach.py # AI coaching system
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.js        # Main app component
│   │   └── index.js      # Entry point
│   └── package.json      # Frontend dependencies
├── backend/              # Flask API backend
│   ├── app.py           # Flask application
│   └── requirements.txt # Backend dependencies
├── tests/               # Test suite
├── main.py             # Original CLI interface
└── environment.yml     # Conda environment
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+
- FFmpeg
- Google Gemini API key

### 1. Backend Setup

```bash
# Create conda environment
conda env create -f environment.yml
conda activate speakeasy

# Install additional backend dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run the backend
python app.py
```

### 2. Frontend Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Start the development server
npm start
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📊 Analysis Features

### Content Quality
- **Clarity Score**: How clear and understandable your message is
- **Relevance Score**: How relevant your content is to the topic
- **Example Usage**: How effectively you use examples and evidence

### Structure & Flow
- **Logical Flow**: How well your ideas connect and build upon each other
- **Transitions**: How smoothly you move between topics
- **Balance**: How well you distribute time across different points

### Vocabulary & Style
- **Lexical Richness**: Diversity and sophistication of your vocabulary
- **Word Appropriateness**: How well your word choices fit the context
- **Repetition Control**: How effectively you avoid unnecessary repetition

### Grammar & Fluency
- **Grammar Correctness**: Accuracy of your grammar and syntax
- **Sentence Fluency**: How smoothly your sentences flow
- **Filler Word Control**: How well you minimize filler words

### Speaking Metrics
- **Word Count**: Total words spoken
- **Words per Minute**: Speaking pace analysis
- **Duration**: Total speech length

## 🎯 AI Coaching

The platform provides personalized feedback including:

- **Strengths**: What you're doing well
- **Areas for Improvement**: Specific suggestions for enhancement
- **Practice Exercises**: Actionable steps to improve your skills
- **Example References**: Links to excellent public speaking examples
- **Context-Aware Tips**: Advice tailored to your speech type and topic

## 🛠️ Development

### Running Tests

```bash
# Run the test suite
python -m unittest discover tests -v
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/build/
```

## 📁 Project Structure

### Models (`models/`)
- **AudioEncoder**: Handles audio feature extraction
- **VideoEncoder**: Processes video content for analysis
- **TextEncoder**: Analyzes transcripts and extracts context
- **Coach**: Provides AI-powered coaching feedback

### Frontend (`frontend/`)
- **React Components**: Modular UI components
- **Video Upload**: Drag & drop file handling
- **Results Display**: Comprehensive analysis visualization
- **Responsive Design**: Mobile-first approach

### Backend (`backend/`)
- **Flask API**: RESTful API endpoints
- **Video Processing**: FFmpeg integration
- **AI Integration**: Google Gemini API
- **File Management**: Secure temporary file handling

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_google_gemini_api_key

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
```

### API Endpoints

- `POST /api/analyze` - Upload and analyze video
- `GET /api/health` - Health check

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is part of the SpeakEasy AI speech analysis platform.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🔮 Future Enhancements

- [ ] Real-time speech analysis
- [ ] Multi-language support
- [ ] Advanced video analytics
- [ ] Integration with video conferencing platforms
- [ ] Mobile app development
- [ ] Team collaboration features