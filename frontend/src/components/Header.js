import React from 'react';

const Header = () => {
  return (
    <header style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      padding: '20px 0',
      marginBottom: '40px',
      borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
    }}>
      <div className="container">
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px'
        }}>
          <div style={{
            fontSize: '32px'
          }}>
            🎤
          </div>
          <h1 style={{
            margin: 0,
            color: 'white',
            fontSize: '2.5rem',
            fontWeight: '700'
          }}>
            SpeakEasy
          </h1>
          <div style={{
            fontSize: '32px'
          }}>
            🚀
          </div>
        </div>
        <p style={{
          textAlign: 'center',
          color: 'rgba(255, 255, 255, 0.9)',
          marginTop: '8px',
          fontSize: '18px'
        }}>
          AI-Powered Speech Analysis & Coaching
        </p>
      </div>
    </header>
  );
};

export default Header;
