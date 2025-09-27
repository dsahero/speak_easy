# SpeakEasy Frontend

A modern React frontend for the SpeakEasy AI speech analysis platform.

## Features

- 🎥 **Video Upload**: Drag & drop or click to upload speech videos
- 📊 **Real-time Analysis**: Live progress tracking during analysis
- 📈 **Detailed Scoring**: Comprehensive breakdown of speech performance
- 🤖 **AI Coach Feedback**: Personalized recommendations and tips
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Building for Production

```bash
npm run build
```

This builds the app for production to the `build` folder.

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js          # App header with branding
│   │   ├── VideoUpload.js     # Video upload and form handling
│   │   └── AnalysisResults.js # Results display and scoring
│   ├── App.js                 # Main app component
│   ├── App.css               # App-specific styles
│   ├── index.js              # React entry point
│   └── index.css             # Global styles
├── package.json
└── README.md
```

## API Integration

The frontend expects a backend API running on `http://localhost:5000` with the following endpoints:

- `POST /api/analyze` - Upload video and get analysis results

### Expected API Response Format

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
  "public_speaking_examples": "Example 1: TED Talk on deep-sea creatures..."
}
```

## Technologies Used

- **React 18** - Modern React with hooks
- **React Dropzone** - File upload with drag & drop
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon library
- **CSS3** - Modern styling with gradients and animations

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

The app uses Create React App with the following scripts:

- `npm start` - Development server
- `npm test` - Run tests
- `npm run build` - Production build
- `npm run eject` - Eject from CRA (not recommended)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the SpeakEasy AI speech analysis platform.
