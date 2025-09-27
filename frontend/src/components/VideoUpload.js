import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Video, FileText, Loader } from 'lucide-react';
import axios from 'axios';

const VideoUpload = ({ onAnalysisComplete, onAnalysisError, isAnalyzing, setIsAnalyzing }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [speechPurpose, setSpeechPurpose] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
      setError(null);
    } else {
      alert('Please select a valid video file.');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
    },
    multiple: false
  });

  const handleAnalyze = async () => {
    if (!selectedFile || !speechPurpose.trim()) {
      alert('Please select a video file and enter the speech purpose.');
      return;
    }

    setIsAnalyzing(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('video', selectedFile);
      formData.append('speech_purpose', speechPurpose);

      const response = await axios.post('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });

      onAnalysisComplete(response.data);
    } catch (error) {
      console.error('Analysis error:', error);
      onAnalysisError(
        error.response?.data?.error || 
        'Failed to analyze video. Please try again.'
      );
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
    } else {
      alert('Please select a valid video file.');
    }
  };

  return (
    <div>
      <div className="upload-section">
        <h2>Upload Your Speech Video</h2>
        <p style={{ marginBottom: '24px', color: '#666' }}>
          Select a video file of your speech to get AI-powered feedback and coaching tips.
        </p>

        <div
          {...getRootProps()}
          className={`upload-area ${isDragActive ? 'dragover' : ''}`}
        >
          <input {...getInputProps()} />
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>
            {isDragActive ? '📁' : '📹'}
          </div>
          <h3 style={{ marginBottom: '8px', color: '#333' }}>
            {isDragActive ? 'Drop your video here' : 'Drag & drop your video here'}
          </h3>
          <p style={{ color: '#666', marginBottom: '16px' }}>
            or click to browse files
          </p>
          <button className="btn btn-secondary">
            <Upload size={20} />
            Choose Video File
          </button>
        </div>

        {selectedFile && (
          <div style={{
            background: '#f8f9fa',
            border: '1px solid #dee2e6',
            borderRadius: '8px',
            padding: '16px',
            margin: '20px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <Video size={24} color="#667eea" />
            <div style={{ flex: 1 }}>
              <p style={{ fontWeight: '600', margin: 0, color: '#333' }}>
                {selectedFile.name}
              </p>
              <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '14px' }}>
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              style={{
                background: 'none',
                border: 'none',
                color: '#dc3545',
                cursor: 'pointer',
                fontSize: '18px'
              }}
            >
              ✕
            </button>
          </div>
        )}

        <div style={{ margin: '24px 0' }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '600',
            color: '#333'
          }}>
            Speech Purpose *
          </label>
          <select
            value={speechPurpose}
            onChange={(e) => setSpeechPurpose(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              fontSize: '16px',
              background: 'white'
            }}
            required
          >
            <option value="">Select the purpose of your speech</option>
            <option value="class presentation">Class Presentation</option>
            <option value="job interview">Job Interview</option>
            <option value="conference talk">Conference Talk</option>
            <option value="wedding speech">Wedding Speech</option>
            <option value="business pitch">Business Pitch</option>
            <option value="debate">Debate</option>
            <option value="storytelling">Storytelling</option>
            <option value="other">Other</option>
          </select>
        </div>

        {isAnalyzing && (
          <div style={{ margin: '24px 0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <Loader className="loading" />
              <span>Analyzing your speech...</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
              This may take a few minutes. Please don't close this page.
            </p>
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={!selectedFile || !speechPurpose || isAnalyzing}
          className="btn"
          style={{ width: '100%', justifyContent: 'center' }}
        >
          {isAnalyzing ? (
            <>
              <Loader className="loading" />
              Analyzing Speech...
            </>
          ) : (
            <>
              <FileText size={20} />
              Analyze My Speech
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default VideoUpload;
