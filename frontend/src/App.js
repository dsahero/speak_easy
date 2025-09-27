import React, { useState } from "react";
import { Upload, BarChart3, RefreshCcw } from "lucide-react";

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      // Simulate API call with fake delay
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Mocked response data
      setAnalysisData({
        clarity: "8/10",
        fillerWords: "Low",
        confidence: "High",
        pace: "Slightly Fast",
      });
      setIsAnalyzing(false);
    } catch (err) {
      setError("Something went wrong while analyzing the video.");
      setIsAnalyzing(false);
    }
  };

  const handleNewAnalysis = () => {
    setAnalysisData(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center px-4">
      {/* Header */}
      <header className="w-full max-w-4xl py-6 text-center">
        <h1 className="text-4xl font-bold tracking-tight mb-2">
          🎤 SpeakEasy AI Coach
        </h1>
        <p className="text-lg text-gray-400">
          Upload your speech video and get AI-powered feedback to sharpen your
          public speaking.
        </p>
      </header>

      {/* Card */}
      <main className="w-full max-w-2xl bg-gray-800 shadow-xl rounded-2xl p-8">
        {!analysisData && !isAnalyzing && (
          <div className="flex flex-col items-center">
            <label className="cursor-pointer flex flex-col items-center justify-center border-2 border-dashed border-gray-600 rounded-xl w-full py-12 hover:bg-gray-700 transition">
              <Upload className="w-12 h-12 text-blue-400 mb-4" />
              <span className="text-gray-300">Click or drag a video here</span>
              <input
                type="file"
                accept="video/*"
                className="hidden"
                onChange={handleFileUpload}
              />
            </label>
          </div>
        )}

        {isAnalyzing && (
          <div className="flex flex-col items-center py-12">
            <RefreshCcw className="w-10 h-10 text-blue-400 animate-spin mb-4" />
            <p className="text-gray-300">Analyzing your speech...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-600/20 border border-red-600 text-red-200 px-4 py-3 rounded-lg">
            <strong>Error:</strong> {error}
          </div>
        )}

        {analysisData && (
          <div>
            <div className="flex items-center mb-6">
              <BarChart3 className="w-6 h-6 text-green-400 mr-2" />
              <h2 className="text-2xl font-semibold">Your Results</h2>
            </div>

            <ul className="space-y-3 mb-8">
              <li className="bg-gray-700 p-4 rounded-xl">
                <strong>Clarity:</strong> {analysisData.clarity}
              </li>
              <li className="bg-gray-700 p-4 rounded-xl">
                <strong>Filler Words:</strong> {analysisData.fillerWords}
              </li>
              <li className="bg-gray-700 p-4 rounded-xl">
                <strong>Confidence:</strong> {analysisData.confidence}
              </li>
              <li className="bg-gray-700 p-4 rounded-xl">
                <strong>Pace:</strong> {analysisData.pace}
              </li>
            </ul>

            <button
              onClick={handleNewAnalysis}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-xl transition"
            >
              Try Another Video
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-8 text-gray-500 text-sm">
        Built with ❤️ using React + Tailwind
      </footer>
    </div>
  );
}

export default App;
