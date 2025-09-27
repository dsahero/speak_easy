import React from 'react';
import { TrendingUp, Clock, Target, MessageCircle, RefreshCw, Star } from 'lucide-react';

const AnalysisResults = ({ data, onNewAnalysis }) => {
  const formatScore = (score) => {
    return Math.round(score * 100);
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#28a745';
    if (score >= 0.6) return '#ffc107';
    return '#dc3545';
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Needs Improvement';
  };

  const renderScoreCard = (title, score, icon) => (
    <div className="score-card" key={title}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        {icon}
        <h4 style={{ margin: 0, color: '#333' }}>{title}</h4>
      </div>
      <div className="score-value" style={{ color: getScoreColor(score) }}>
        {formatScore(score)}%
      </div>
      <div className="score-label">
        {getScoreLabel(score)}
      </div>
    </div>
  );

  return (
    <div className="results-section">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2>Analysis Results</h2>
        <button onClick={onNewAnalysis} className="btn btn-secondary">
          <RefreshCw size={20} />
          Analyze Another Video
        </button>
      </div>

      {/* Overall Score */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderRadius: '16px',
        padding: '32px',
        textAlign: 'center',
        marginBottom: '32px'
      }}>
        <h3 style={{ color: 'white', marginBottom: '16px' }}>Overall Performance</h3>
        <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '8px' }}>
          {data.overall_score ? formatScore(data.overall_score) : 'N/A'}%
        </div>
        <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '18px' }}>
          {data.overall_score ? getScoreLabel(data.overall_score) : 'Analysis in progress...'}
        </p>
      </div>

      {/* Detailed Scores */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Target size={24} />
          Detailed Analysis
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          {data.transcript_scores && (
            <>
              {data.transcript_scores.content_quality && (
                <div>
                  <h4 style={{ marginBottom: '12px', color: '#333' }}>Content Quality</h4>
                  {renderScoreCard('Clarity', data.transcript_scores.content_quality.clarity_score, <MessageCircle size={20} />)}
                  {renderScoreCard('Relevance', data.transcript_scores.content_quality.relevance_score, <Target size={20} />)}
                  {renderScoreCard('Examples Usage', data.transcript_scores.content_quality.example_usage_score, <Star size={20} />)}
                </div>
              )}

              {data.transcript_scores.structure && (
                <div>
                  <h4 style={{ marginBottom: '12px', color: '#333' }}>Structure</h4>
                  {renderScoreCard('Logical Flow', data.transcript_scores.structure.logical_flow_score, <TrendingUp size={20} />)}
                  {renderScoreCard('Transitions', data.transcript_scores.structure.transition_score, <TrendingUp size={20} />)}
                  {renderScoreCard('Balance', data.transcript_scores.structure.balance_score, <Target size={20} />)}
                </div>
              )}

              {data.transcript_scores.vocabulary_style && (
                <div>
                  <h4 style={{ marginBottom: '12px', color: '#333' }}>Vocabulary & Style</h4>
                  {renderScoreCard('Lexical Richness', data.transcript_scores.vocabulary_style.lexical_richness, <MessageCircle size={20} />)}
                  {renderScoreCard('Word Appropriateness', data.transcript_scores.vocabulary_style.word_appropriateness, <Target size={20} />)}
                  {renderScoreCard('Repetition Control', data.transcript_scores.vocabulary_style.repetition_score, <TrendingUp size={20} />)}
                </div>
              )}

              {data.transcript_scores.grammar_fluency && (
                <div>
                  <h4 style={{ marginBottom: '12px', color: '#333' }}>Grammar & Fluency</h4>
                  {renderScoreCard('Grammar Correctness', data.transcript_scores.grammar_fluency.grammar_correctness, <MessageCircle size={20} />)}
                  {renderScoreCard('Sentence Fluency', data.transcript_scores.grammar_fluency.sentence_fluency, <TrendingUp size={20} />)}
                  {renderScoreCard('Filler Word Control', data.transcript_scores.grammar_fluency.filler_word_density, <Target size={20} />)}
                </div>
              )}

              {data.transcript_scores.speaking_length && (
                <div>
                  <h4 style={{ marginBottom: '12px', color: '#333' }}>Speaking Length</h4>
                  <div style={{ background: '#f8f9fa', padding: '16px', borderRadius: '8px' }}>
                    <p><strong>Word Count:</strong> {data.transcript_scores.speaking_length.word_count}</p>
                    <p><strong>Words per Minute:</strong> {Math.round(data.transcript_scores.speaking_length.words_per_minute)}</p>
                    <p><strong>Duration:</strong> {Math.round(data.transcript_scores.video_duration_seconds / 60)} minutes</p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Speech Context */}
      {data.speech_context && (
        <div className="feedback-section">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={24} />
            Speech Context
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div>
              <strong>Specific Topic:</strong>
              <p style={{ margin: '4px 0 0 0', color: '#666' }}>{data.speech_context.specific_topic}</p>
            </div>
            <div>
              <strong>General Topic:</strong>
              <p style={{ margin: '4px 0 0 0', color: '#666' }}>{data.speech_context.general_topic}</p>
            </div>
            <div>
              <strong>Format:</strong>
              <p style={{ margin: '4px 0 0 0', color: '#666' }}>{data.speech_context.format}</p>
            </div>
          </div>
        </div>
      )}

      {/* AI Coach Feedback */}
      {data.coach_feedback && (
        <div className="feedback-section">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MessageCircle size={24} />
            AI Coach Feedback
          </h3>
          <div className="feedback-content">
            {data.coach_feedback.split('\n').map((paragraph, index) => (
              <p key={index} style={{ marginBottom: '12px' }}>
                {paragraph}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Public Speaking Examples */}
      {data.public_speaking_examples && (
        <div className="feedback-section">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Star size={24} />
            Recommended Examples
          </h3>
          <div className="feedback-content">
            {data.public_speaking_examples.split('\n').map((example, index) => (
              <p key={index} style={{ marginBottom: '8px' }}>
                {example}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '16px', marginTop: '32px', justifyContent: 'center' }}>
        <button onClick={onNewAnalysis} className="btn">
          <RefreshCw size={20} />
          Analyze Another Video
        </button>
        <button 
          onClick={() => window.print()} 
          className="btn btn-secondary"
        >
          <MessageCircle size={20} />
          Print Results
        </button>
      </div>
    </div>
  );
};

export default AnalysisResults;
