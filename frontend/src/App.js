import React, { useState, useCallback, useRef, useEffect } from 'react';

// --- SVG Icons (as components for better reusability) ---
const UploadCloudIcon = ({ className }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" /><path d="M12 12v9" /><path d="m16 16-4-4-4 4" />
  </svg>
);

const FileVideoIcon = ({ className }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
        <polyline points="14 2 14 8 20 8" />
        <path d="m10 15.5 4 2.5v-6l-4 2.5" />
    </svg>
);

const BrainCircuitIcon = ({ className }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2a10 10 0 0 0-10 10c0 1.85.54 3.58 1.45 5.05A10 10 0 0 0 12 22a10 10 0 0 0 8.55-4.95A10 10 0 0 0 22 12a10 10 0 0 0-10-10Z" />
        <path d="M12 12a2.5 2.5 0 0 0-2.5 2.5c0 1.41.83 2.62 2 3.16V22" />
        <path d="M12 12a2.5 2.5 0 0 1 2.5 2.5c0 1.41-.83 2.62-2 3.16V22" />
        <path d="M12 12a2.5 2.5 0 0 0-2.5-2.5c0-1.41.83-2.62 2-3.16V2" />
        <path d="M12 12a2.5 2.5 0 0 1 2.5-2.5c0-1.41-.83-2.62-2-3.16V2" />
        <path d="M14.5 4.95A2.5 2.5 0 0 0 12 7.5c-1.41 0-2.62-.83-3.16-2" />
        <path d="M9.5 19.05A2.5 2.5 0 0 0 12 16.5c1.41 0 2.62.83 3.16 2" />
        <path d="M4.95 9.5A2.5 2.5 0 0 0 7.5 12c0 1.41-.83 2.62-2 3.16" />
        <path d="M19.05 14.5A2.5 2.5 0 0 0 16.5 12c0-1.41.83-2.62 2-3.16" />
    </svg>
);

const AlertTriangleIcon = ({ className }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m21.73 18-8-14a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" /><line x1="12" x2="12" y1="9" y2="13" /><line x1="12" x2="12.01" y1="17" y2="17" />
    </svg>
);

const ThumbsUpIcon = ({ className }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M7 10v12" /><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z" />
    </svg>
);

const TrendingUpIcon = ({ className }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" />
    </svg>
);

const VideoIcon = ({ className }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m22 8-6 4 6 4V8Z"/><path d="M14 22H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2Z"/>
    </svg>
);


// --- Mock API and Data ---
const mockAnalysisData = {
    contentQuality: { clarityScore: 85, relevanceScore: 92, exampleUsage: 78 },
    structureFlow: { logicalFlow: 88, transitions: 75, balance: 82 },
    vocabularyStyle: { lexicalRichness: 90, wordAppropriateness: 95, repetitionControl: 80 },
    grammarFluency: { grammarCorrectness: 98, sentenceFluency: 87, fillerWordControl: 70 },
    speakingMetrics: { wordCount: 1245, wordsPerMinute: 155, duration: "8m 2s" },
    aiCoaching: {
        strengths: ["Excellent use of specific data to support your main points.", "Your tone was engaging and confident throughout the presentation.", "Great job maintaining eye contact with the camera, which translates to the audience."],
        areasForImprovement: ["Try to reduce the use of filler words like 'um' and 'ah', especially during transitions.", "Some sections could benefit from clearer signposting to guide the listener.", "Consider varying your vocal pitch more to add emphasis to key ideas."],
        practiceExercises: ["Record yourself practicing the transitions between your main points.", "Try the 'one-minute impromptu' exercise daily on a random topic to improve fluency."],
    },
};

// const analyzeAPI = async (file, onProgress) => {
//     // Create form data
//     const formData = new FormData();
//     formData.append("file", file);

//     // Use XMLHttpRequest to track upload progress
//     return new Promise((resolve, reject) => {
//         const xhr = new XMLHttpRequest();
//         xhr.open("POST", "http://localhost:5000/process");

//         xhr.upload.onprogress = (event) => {
//             if (event.lengthComputable) {
//                 const percentComplete = (event.loaded / event.total) * 100;
//                 onProgress(percentComplete);
//             }
//         };

//         xhr.onload = () => {
//             if (xhr.status === 200) {
//                 const data = JSON.parse(xhr.responseText);
//                 resolve(data.results);
//             } else {
//                 reject(new Error(`Upload failed: ${xhr.statusText}`));
//             }
//         };

//         xhr.onerror = () => reject(new Error("Network error"));
//         xhr.send(formData);
//     });
// };

// const analyzeAPI = async (file, onProgress) => {
//     const formData = new FormData();
//     formData.append("file", file);

//     return new Promise((resolve, reject) => {
//         const xhr = new XMLHttpRequest();
//         xhr.open("POST", "http://localhost:5000/process");

//         xhr.upload.onprogress = (event) => {
//             if (event.lengthComputable) {
//                 const percentComplete = (event.loaded / event.total) * 100;
//                 onProgress(percentComplete);
//             }
//         };
//         xhr.onload = () => {
//             if (xhr.status === 200) {
//                 const data = JSON.parse(xhr.responseText);
//                 const { audio_grades, text_grades, context, examples } = data.results;

//                 // 🔍 Debugging logs
//                 console.log("Raw text_grades:", text_grades);
//                 console.log("Clarity score raw:", text_grades.clarity_score);
//                 console.log("Relevance score raw:", text_grades.relevance_score);
//                 console.log("Example usage raw:", text_grades.example_usage_score);
//                 console.log("Raw audio_grades:", audio_grades);

//                 // Safely parse numbers
//                 const clarityScore = Number(text_grades.clarity_score || 0);
//                 const relevanceScore = Number(text_grades.relevance_score || 0);
//                 const exampleUsage = Number(text_grades.example_usage_score || 0);

//                 const logicalFlow = Number(text_grades.logical_flow_score || 0);
//                 const transitions = Number(text_grades.transition_score || 0);
//                 const balance = Number(text_grades.balance_score || 0);

//                 const lexicalRichness = Number(text_grades.lexical_richness || 0);
//                 const wordAppropriateness = Number(text_grades.word_appropriateness || 0);
//                 const repetitionControl = Number(text_grades.repetition_score || 0);

//                 const grammarCorrectness = Number(text_grades.grammar_correctness || 0);
//                 const sentenceFluency = Number(text_grades.sentence_fluency || 0);
//                 const fillerWordControl = Number(audio_grades.filler_word_control || 0);

//                 const formattedData = {
//                     contentQuality: {
//                         clarityScore: Math.round(clarityScore * 100),
//                         relevanceScore: Math.round(relevanceScore * 100),
//                         exampleUsage: Math.round(exampleUsage * 100),
//                     },
//                     structureFlow: {
//                         logicalFlow: Math.round(logicalFlow * 100),
//                         transitions: Math.round(transitions * 100),
//                         balance: Math.round(balance * 100),
//                     },
//                     vocabularyStyle: {
//                         lexicalRichness: Math.round(lexicalRichness * 100),
//                         wordAppropriateness: Math.round(wordAppropriateness * 100),
//                         repetitionControl: Math.round(repetitionControl * 100),
//                     },
//                     grammarFluency: {
//                         grammarCorrectness: Math.round(grammarCorrectness * 100),
//                         sentenceFluency: Math.round(sentenceFluency * 100),
//                         fillerWordControl: Math.round(fillerWordControl * 100),
//                     },
//                     speakingMetrics: {
//                         wordCount: audio_grades.word_count || 0,
//                         wordsPerMinute: audio_grades.words_per_minute || 0,
//                         duration: audio_grades.duration || "0:00",
//                     },
//                     aiCoaching: {
//                         strengths: audio_grades.areas_for_improvement
//                             ? audio_grades.areas_for_improvement.slice(0, 3)
//                             : ["Great clarity and confidence!"],
//                         areasForImprovement: audio_grades.areas_for_improvement || [],
//                         practiceExercises: [
//                             "Practice your speech in front of a mirror.",
//                             "Record yourself and listen to improve pacing and tone.",
//                         ],
//                     },
//                 };

//                 resolve(formattedData);
//             } else {
//                 reject(new Error(`Upload failed: ${xhr.statusText}`));
//             }
//         };
    


// //         xhr.onload = () => {
// //             if (xhr.status === 200) {
// //                 const data = JSON.parse(xhr.responseText);
// //                 const { audio_grades, text_grades, context, examples } = data.results;

// //                 // Transform backend data into the mockAnalysisData format
// //                 const formattedData = {
// //                     contentQuality: {
// //                         clarityScore: Math.round((text_grades["clarity_score"] || 0) * 100),
// //                         relevanceScore: Math.round((text_grades.relevance_score || 0) * 100),
// //                         exampleUsage: Math.round((text_grades.example_usage_score || 0) * 100),
// //                     },
// //                     structureFlow: {
// //                         logicalFlow: Math.round((text_grades.logical_flow_score || 0) * 100),
// //                         transitions: Math.round((text_grades.transition_score || 0) * 100),
// //                         balance: Math.round((text_grades.balance_score || 0) * 100),
// //                     },
// //                     vocabularyStyle: {
// //                         lexicalRichness: Math.round((text_grades.lexical_richness || 0) * 100),
// //                         wordAppropriateness: Math.round((text_grades.word_appropriateness || 0) * 100),
// //                         repetitionControl: Math.round((text_grades.repetition_score || 0) * 100),
// //                     },
// //                     grammarFluency: {
// //                         grammarCorrectness: Math.round((text_grades.grammar_correctness || 0) * 100),
// //                         sentenceFluency: Math.round((text_grades.sentence_fluency || 0) * 100),
// //                         fillerWordControl: Math.round(((audio_grades.filler_word_control || 0)) * 100),
// //                     },
// //                     speakingMetrics: {
// //                         wordCount: audio_grades.word_count || 0,
// //                         wordsPerMinute: audio_grades.words_per_minute || 0,
// //                         duration: audio_grades.duration || "0:00",
// //                     },
// //                     aiCoaching: {
// //                         strengths: audio_grades.areas_for_improvement
// //                             ? audio_grades.areas_for_improvement.slice(0, 3)
// //                             : ["Great clarity and confidence!"],
// //                         areasForImprovement: audio_grades.areas_for_improvement || [],
// //                         practiceExercises: [
// //                             "Practice your speech in front of a mirror.",
// //                             "Record yourself and listen to improve pacing and tone.",
// //                         ],
// //                     },
// //                 };

// //                 resolve(formattedData);
// //             } else {
// //                 reject(new Error(`Upload failed: ${xhr.statusText}`));
// //             }
// //         };

//         xhr.onerror = () => reject(new Error("Network error"));
//         xhr.send(formData);
//     });
// };

const analyzeAPI = async (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:5000/process");

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100;
        onProgress(percentComplete);
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        const { audio_grades, text_grades } = data.results;

        // Text grades mapping
        const clarityScore = Number(text_grades.content_quality.clarity_score || 0);
        const relevanceScore = Number(text_grades.content_quality.relevance_score || 0);
        const exampleUsage = Number(text_grades.content_quality.example_usage_score || 0);

        const logicalFlow = Number(text_grades.structure.logical_flow_score || 0);
        const transitions = Number(text_grades.structure.transition_score || 0);
        const balance = Number(text_grades.structure.balance_score || 0);

        const lexicalRichness = Number(text_grades.vocabulary_style.lexical_richness || 0);
        const wordAppropriateness = Number(text_grades.vocabulary_style.word_appropriateness || 0);
        const repetitionControl = Number(text_grades.vocabulary_style.repetition_score || 0);

        const grammarCorrectness = Number(text_grades.grammar_fluency.grammar_correctness || 0);
        const sentenceFluency = Number(text_grades.grammar_fluency.sentence_fluency || 0);
        const fillerWordControl = Number(text_grades.grammar_fluency.filler_word_density || 0);

        const formattedData = {
            contentQuality: {
                clarityScore: Math.round(clarityScore * 100),
                relevanceScore: Math.round(relevanceScore * 100),
                exampleUsage: Math.round(exampleUsage * 100),
            },
            structureFlow: {
                logicalFlow: Math.round(logicalFlow * 100),
                transitions: Math.round(transitions * 100),
                balance: Math.round(balance * 100),
            },
            vocabularyStyle: {
                lexicalRichness: Math.round(lexicalRichness * 100),
                wordAppropriateness: Math.round(wordAppropriateness * 100),
                repetitionControl: Math.round(repetitionControl * 100),
            },
            grammarFluency: {
                grammarCorrectness: Math.round(grammarCorrectness * 100),
                sentenceFluency: Math.round(sentenceFluency * 100),
                fillerWordControl: Math.round(fillerWordControl * 100),
            },
            speakingMetrics: {
                wordCount: audio_grades.word_count || 0,
                wordsPerMinute: audio_grades.words_per_minute || 0,
                duration: audio_grades.duration || "0:00",
            },
                    aiCoaching: {
                        strengths: audio_grades.areas_for_improvement
                            ? audio_grades.areas_for_improvement.slice(0, 3)
                            : ["Great clarity and confidence!"],
                        areasForImprovement: audio_grades.areas_for_improvement || [],
                        practiceExercises: [
                            "Practice your speech in front of a mirror.",
                            "Record yourself and listen to improve pacing and tone.",
                        ],
                    },
                };

                resolve(formattedData);
            } else {
                reject(new Error(`Upload failed: ${xhr.statusText}`));
            }
        };

        xhr.onerror = () => reject(new Error("Network error"));
        xhr.send(formData);
    });
};


// --- UI Components ---

const Header = ({ view, setView }) => (
    <header className="bg-gray-900 text-white shadow-md">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
                <div className="flex items-center">
                    <BrainCircuitIcon className="h-8 w-8 text-indigo-400" />
                    <h1 className="ml-3 text-2xl font-bold tracking-tight">SpeakEasy</h1>
                </div>
                <nav className="flex items-center space-x-2 rounded-lg p-1 bg-gray-800">
                    <button onClick={() => setView('upload')} className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${view === 'upload' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`}>
                        Upload Video
                    </button>
                    <button onClick={() => setView('live')} className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${view === 'live' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`}>
                        Live Practice
                    </button>
                </nav>
            </div>
        </div>
    </header>
);

const ProgressBar = ({ value, label }) => {
    const getColor = (val) => {
        if (val < 50) return 'bg-red-500';
        if (val < 80) return 'bg-yellow-500';
        return 'bg-green-500';
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-gray-300">{label}</span>
                <span className={`text-sm font-bold ${getColor(value).replace('bg-', 'text-')}`}>{value}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div className={`${getColor(value)} h-2.5 rounded-full`} style={{ width: `${value}%` }}></div>
            </div>
        </div>
    );
};

const ScoreCard = ({ title, scores }) => (
    <div className="bg-gray-800 rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
        <div className="space-y-4">
            {Object.entries(scores).map(([key, value]) => {
                 const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
                 return <ProgressBar key={key} label={label} value={value} />;
            })}
        </div>
    </div>
);

const MetricCard = ({ label, value }) => (
    <div className="bg-gray-800 rounded-xl shadow-lg p-4 text-center">
        <p className="text-sm text-gray-400">{label}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
    </div>
);

const CoachingCard = ({ title, items, icon, colorClass }) => (
    <div className="bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center mb-3">
            {icon}
            <h3 className={`ml-3 text-lg font-semibold ${colorClass}`}>{title}</h3>
        </div>
        <ul className="list-disc list-inside space-y-2 text-gray-300">
            {items.map((item, index) => <li key={index}>{item}</li>)}
        </ul>
    </div>
);

const VideoUpload = ({ onUpload, setFile, file, error, setError }) => {
    const [isDragging, setIsDragging] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            processFile(selectedFile);
        }
    };
    
    const processFile = (selectedFile) => {
        setError(null);
        if (selectedFile && selectedFile.type.startsWith('video/')) {
            setFile(selectedFile);
        } else {
            setError('Please upload a valid video file.');
        }
    };

    const handleDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files?.[0];
        if (droppedFile) {
            processFile(droppedFile);
        }
    };
    
    const handleSubmit = () => {
        if (file) {
            onUpload(file);
        }
    }

    return (
        <div className="w-full max-w-2xl mx-auto">
            <div
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl p-8 sm:p-12 text-center transition-colors duration-300 ${isDragging ? 'border-indigo-400 bg-gray-800' : 'border-gray-600 hover:border-gray-500'}`}
            >
                <div className="flex flex-col items-center text-gray-400">
                    <UploadCloudIcon className="w-16 h-16 mb-4" />
                    <p className="text-xl font-semibold">Drag & drop your video here</p>
                    <p className="text-sm mt-2">or</p>
                    <label htmlFor="file-upload" className="mt-4 cursor-pointer inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500">
                        Browse Files
                    </label>
                    <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="video/*" onChange={handleFileChange} />
                </div>
            </div>

            {error && (
                <div className="mt-4 flex items-center text-red-400 bg-red-900/20 p-3 rounded-lg">
                    <AlertTriangleIcon className="w-5 h-5 mr-2"/>
                    <span className="text-sm">{error}</span>
                </div>
            )}

            {file && !error && (
                <div className="mt-6 bg-gray-800 p-4 rounded-lg flex items-center justify-between">
                    <div className="flex items-center min-w-0">
                        <FileVideoIcon className="w-8 h-8 text-indigo-400 flex-shrink-0" />
                        <div className="ml-4 min-w-0">
                            <p className="text-sm font-medium text-white truncate">{file.name}</p>
                            <p className="text-xs text-gray-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                        </div>
                    </div>
                    <button
                        onClick={handleSubmit}
                        className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-green-500 disabled:bg-gray-500 disabled:cursor-not-allowed flex-shrink-0 ml-4"
                    >
                        Analyze
                    </button>
                </div>
            )}
        </div>
    );
};

const AnalysisInProgress = ({ uploadProgress, status, statusMessage }) => (
    <div className="w-full max-w-2xl mx-auto text-center py-12">
        {status === 'uploading' && (
            <>
                <h2 className="text-2xl font-semibold text-white mb-4">Uploading Video...</h2>
                <div className="w-full bg-gray-700 rounded-full h-4">
                    <div
                        className="bg-indigo-600 h-4 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${uploadProgress}%` }}
                    ></div>
                </div>
                <p className="text-white mt-4 text-lg">{Math.round(uploadProgress)}%</p>
            </>
        )}
        {status === 'analyzing' && (
            <>
                <div className="flex justify-center items-center mb-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400"></div>
                </div>
                <h2 className="text-2xl font-semibold text-white">Analyzing Speech...</h2>
                <p className="text-gray-400 mt-2">
                    {statusMessage || "Our AI is processing your video. This may take a moment."}
                </p>
            </>
        )}
    </div>
);


const AnalysisResults = ({ results, onReset }) => (
    <div className="max-w-7xl mx-auto py-8">
        <div className="text-center mb-10">
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">Your Speech Analysis Results</h2>
            <p className="mt-4 text-lg text-gray-400">Here's the breakdown of your performance.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
                <ScoreCard title="Content Quality" scores={results.contentQuality} />
                <ScoreCard title="Structure & Flow" scores={results.structureFlow} />
                <ScoreCard title="Vocabulary & Style" scores={results.vocabularyStyle} />
                <ScoreCard title="Grammar & Fluency" scores={results.grammarFluency} />
            </div>

            <div className="space-y-8">
                <div>
                    <h3 className="text-lg font-semibold text-white mb-4">Speaking Metrics</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <MetricCard label="Word Count" value={results.speakingMetrics.wordCount} />
                        <MetricCard label="WPM" value={results.speakingMetrics.wordsPerMinute} />
                        <div className="col-span-2">
                           <MetricCard label="Duration" value={results.speakingMetrics.duration} />
                        </div>
                    </div>
                </div>
                <div>
                       <h3 className="text-lg font-semibold text-white mb-4">AI Coaching</h3>
                       <div className="space-y-6">
                            <CoachingCard 
                                title="Strengths" 
                                items={results.aiCoaching.strengths} 
                                icon={<ThumbsUpIcon className="w-6 h-6 text-green-400"/>}
                                colorClass="text-green-400"
                            />
                             <CoachingCard 
                                title="Areas for Improvement" 
                                items={results.aiCoaching.areasForImprovement}
                                icon={<TrendingUpIcon className="w-6 h-6 text-yellow-400"/>}
                                colorClass="text-yellow-400"
                            />
                             <CoachingCard 
                                title="Practice Exercises" 
                                items={results.aiCoaching.practiceExercises}
                                icon={<BrainCircuitIcon className="w-6 h-6 text-indigo-400"/>}
                                colorClass="text-indigo-400"
                            />
                       </div>
                </div>
            </div>
        </div>
        <div className="text-center mt-12">
            <button
                onClick={onReset}
                className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500"
            >
                {results.from === 'live' ? 'Practice Again' : 'Analyze Another Video'}
            </button>
        </div>
    </div>
);

const LivePractice = () => {
    const [elapsedTime, setElapsedTime] = useState(0);
    const [practiceStatus, setPracticeStatus] = useState('idle'); // idle, recording, analyzing, success
    const [practiceAnalysisResult, setPracticeAnalysisResult] = useState(null);
    const [mediaError, setMediaError] = useState(null);

    const videoRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const streamRef = useRef(null);
    const recordedChunksRef = useRef([]);
    const timerIntervalRef = useRef(null);

    const formatTime = (totalSeconds) => {
        const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
        const seconds = (totalSeconds % 60).toString().padStart(2, '0');
        return `${minutes}:${seconds}`;
    };

    const startPractice = async () => {
        setMediaError(null);
        recordedChunksRef.current = [];
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
            
            mediaRecorderRef.current = new MediaRecorder(stream);

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    recordedChunksRef.current.push(event.data);
                }
            };
            
            mediaRecorderRef.current.onstop = () => {
                const videoBlob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
                console.log("Recording complete, blob created:", videoBlob);
                setPracticeStatus('analyzing');
                setTimeout(() => {
                    setPracticeAnalysisResult({...mockAnalysisData, from: 'live'});
                    setPracticeStatus('success');
                }, 3000); 
            };

            mediaRecorderRef.current.start();
            setPracticeStatus('recording');
            setElapsedTime(0);
            
            timerIntervalRef.current = setInterval(() => {
                setElapsedTime(prev => prev + 1);
            }, 1000);

        } catch (error) {
            console.error("Error accessing camera/microphone:", error);
            setMediaError("Could not access camera/microphone. Please check permissions and refresh.");
        }
    };

    const stopPractice = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.stop();
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }
        if(timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
    
    const handleResetPractice = () => {
        setPracticeStatus('idle');
        setPracticeAnalysisResult(null);
        setElapsedTime(0);
    };

    useEffect(() => {
        return () => {
            if(timerIntervalRef.current) clearInterval(timerIntervalRef.current);
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    if (practiceStatus === 'success') {
        return <AnalysisResults results={practiceAnalysisResult} onReset={handleResetPractice} />;
    }

    if (practiceStatus === 'analyzing') {
        return (
             <div className="w-full max-w-2xl mx-auto text-center py-12">
                <div className="flex justify-center items-center mb-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400"></div>
                </div>
                <h2 className="text-2xl font-semibold text-white">Analyzing Your Practice...</h2>
                <p className="text-gray-400 mt-2">This may take a moment.</p>
            </div>
        )
    }

    return (
        <div className="max-w-4xl mx-auto py-8">
            <div className="text-center mb-10">
                <h2 className="text-3xl font-extrabold text-white sm:text-4xl">Live Practice Session</h2>
                <p className="mt-4 text-lg text-gray-400">Record yourself and get a full analysis report.</p>
            </div>

            <div className="bg-gray-800 rounded-xl shadow-lg p-6 flex flex-col items-center justify-center space-y-6">
                <div className="w-full aspect-video bg-black rounded-lg overflow-hidden relative">
                    <video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover"></video>
                     {practiceStatus === 'idle' && !mediaError && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                            <p className="text-white text-lg font-medium">Camera feed will appear here</p>
                        </div>
                    )}
                </div>
                
                {practiceStatus === 'recording' && (
                       <div className="text-center">
                            <p className="text-lg text-gray-400">Elapsed Time</p>
                            <p className="text-6xl font-bold tracking-tighter text-white">{formatTime(elapsedTime)}</p>
                        </div>
                )}

                <button
                    onClick={practiceStatus === 'recording' ? stopPractice : startPractice}
                    className={`w-full max-w-xs py-3 px-6 text-lg font-bold rounded-lg transition-all flex items-center justify-center ${practiceStatus === 'recording' ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}`}
                >
                    <VideoIcon className="w-6 h-6 mr-3" />
                    {practiceStatus === 'recording' ? 'Stop & Analyze' : 'Start Recording'}
                </button>
                {mediaError && <p className="text-red-400 text-sm text-center mt-2">{mediaError}</p>}
            </div>
        </div>
    );
};


function App() {
    const [view, setView] = useState('upload'); // 'upload' or 'live'
    const [status, setStatus] = useState('idle'); // idle, uploading, analyzing, success, error
    const [file, setFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [error, setError] = useState(null);
    const [statusMessage, setStatusMessage] = useState('');
    
    const handleUpload = useCallback(async (videoFile) => {
    setStatus('uploading');
    setUploadProgress(0);
    setError(null);
    setStatusMessage('');

    try {
        const result = await analyzeAPI(videoFile, (progress, message) => {
            setUploadProgress(progress);

            // ✅ Only update statusMessage if provided by API
            if (message) setStatusMessage(message);

            if (progress >= 100) {
                setStatus('analyzing');
            }
        });

        setAnalysisResult(result);
        setStatus('success');
    } catch (err) {
        setError(err.message);
        setStatus('error');
    }
}, []);


    const handleReset = () => {
        setStatus('idle');
        setFile(null);
        setUploadProgress(0);
        setAnalysisResult(null);
        setError(null);
    };

    const renderContent = () => {
    if (view === 'live') {
        return <LivePractice />;
    }

    switch (status) {
        case 'uploading':
        case 'analyzing':
            return (
                <AnalysisInProgress
                    uploadProgress={uploadProgress}
                    status={status}
                    statusMessage={statusMessage} // ✅ pass statusMessage here
                />
            );
        case 'success':
            return <AnalysisResults results={analysisResult} onReset={handleReset} />;
        case 'error':
            return (
                <div className="py-8">
                    <div className="mb-6 flex items-center text-red-400 bg-red-900/20 p-4 rounded-lg max-w-2xl mx-auto">
                        <AlertTriangleIcon className="w-6 h-6 mr-3 flex-shrink-0"/>
                        <div>
                            <h3 className="font-semibold">Analysis Failed</h3>
                            <p className="text-sm">{error}</p>
                        </div>
                    </div>
                    <VideoUpload
                        onUpload={handleUpload}
                        setFile={setFile}
                        file={file}
                        error={null}
                        setError={setError}
                    />
                </div>
            );
        case 'idle':
        default:
            return (
                <div className="py-12 sm:py-20">
                    <h2 className="text-3xl font-extrabold text-white text-center sm:text-4xl">Upload Your Speech</h2>
                    <p className="mt-4 text-lg text-gray-400 text-center">Get instant AI-powered feedback to improve your public speaking.</p>
                    <div className="mt-10">
                        <VideoUpload
                            onUpload={handleUpload}
                            setFile={setFile}
                            file={file}
                            error={error}
                            setError={setError}
                        />
                    </div>
                </div>
            );
    }
};



    return (
        <div className="bg-gray-900 text-white min-h-screen font-sans flex flex-col">
            <Header view={view} setView={setView} />
            <main className="container mx-auto px-4 sm:px-6 lg:px-8 flex-grow">
                {renderContent()}
            </main>
            <footer className="bg-gray-900 mt-auto py-6">
                <div className="text-center text-gray-500 text-sm">
                    © {new Date().getFullYear()} SpeakEasy. AI Speech Analysis Platform.
                </div>
            </footer>
        </div>
    );
}

export default App;