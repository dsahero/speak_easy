import React, { useState } from 'react';
import VideoUpload from './components/VideoUpload';
import AnalysisResults from './components/AnalysisResults';
import Header from './components/Header';
import './App.css';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    setIsAnalyzing(false);
    setError(null);
  };

  const handleAnalysisError = (errorMessage) => {
    setError(errorMessage);
    setIsAnalyzing(false);
  };

  const handleNewAnalysis = () => {
    setAnalysisData(null);
    setError(null);
  };

  return (
    <div className="App">
      <Header />
      <div className="container">
        <div className="card">
          <h1 style={{ textAlign: 'center', marginBottom: '32px', color: '#333' }}>
            🎤 SpeakEasy AI Coach
          </h1>
          <p style={{ textAlign: 'center', color: '#666', marginBottom: '32px', fontSize: '18px' }}>
            Upload your speech video and get AI-powered feedback to improve your public speaking skills
          </p>
          
          {!analysisData && (
            <VideoUpload 
              onAnalysisComplete={handleAnalysisComplete}
              onAnalysisError={handleAnalysisError}
              isAnalyzing={isAnalyzing}
              setIsAnalyzing={setIsAnalyzing}
            />
          )}
          
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}
          
          {analysisData && (
            <AnalysisResults 
              data={analysisData}
              onNewAnalysis={handleNewAnalysis}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
