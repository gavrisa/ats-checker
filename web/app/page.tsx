'use client';

import { useState } from 'react';
import { Upload, Search, FileText, CheckCircle, AlertCircle, RefreshCw, BarChart3 } from 'lucide-react';
import { config } from '../config';

// Force Vercel to use latest code with TypeScript fixes
// Build timestamp: 2024-08-30 02:53 UTC - All TypeScript errors resolved
export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'failed'>('checking');
  const [debugInfo, setDebugInfo] = useState<string>('');

  // Test backend connection
  const testConnection = async () => {
    try {
      setConnectionStatus('checking');
      const response = await fetch(`${config.backendUrl}${config.endpoints.health}`);
      if (response.ok) {
        const data = await response.json();
        setConnectionStatus('connected');
        setDebugInfo(`✅ Backend connected! Health: ${JSON.stringify(data)}`);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      setConnectionStatus('failed');
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setDebugInfo(`❌ Connection failed: ${errorMessage}`);
    }
  };

  // Handle file drop
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && config.allowedFileTypes.some(type => droppedFile.name.toLowerCase().endsWith(type))) {
      setFile(droppedFile);
    }
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  // Analyze resume
  const analyzeResume = async () => {
    if (!file || !jobDescription.trim()) return;

    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('resume_file', file);
    formData.append('job_description', jobDescription);

    try {
      const response = await fetch(`${config.backendUrl}${config.endpoints.analyze}`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setResults({ error: errorMessage });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="h-8 w-8 text-blue-600" />
            <h1 className="text-2xl font-ibm-condensed font-extralight text-gray-800">
              ATS Resume Checker
            </h1>
          </div>
          <button
            onClick={testConnection}
            className={`px-4 py-2 rounded-lg font-ibm-condensed font-extralight text-sm transition-colors ${
              connectionStatus === 'connected'
                ? 'bg-green-100 text-green-700'
                : connectionStatus === 'failed'
                ? 'bg-red-100 text-red-700'
                : 'bg-blue-100 text-blue-700'
            }`}
          >
            {connectionStatus === 'checking' && <RefreshCw className="h-4 w-4 animate-spin mr-2" />}
            {connectionStatus === 'connected' && <CheckCircle className="h-4 w-4 mr-2" />}
            {connectionStatus === 'failed' && <AlertCircle className="h-4 w-4 mr-2" />}
            {connectionStatus === 'checking' ? 'Testing...' : connectionStatus === 'connected' ? 'Connected' : 'Failed'}
          </button>
        </div>
      </header>

      <div className="flex h-screen">
        {/* Left Panel - Input Section */}
        <div className="w-full lg:w-1/2 bg-[#F2F2F2] pl-8 md:pl-12 lg:pl-16 xl:pl-20 2xl:pl-24 pr-8 md:pr-12 lg:pr-16 xl:pr-20 2xl:pr-24 pt-8 pb-8 overflow-hidden">
          <div className="max-w-md mx-auto">
            {/* Main Heading */}
            <h2 className="text-5xl font-ibm-condensed font-extralight text-black mb-6 leading-tight">
              Is your resume ATS-ready?
            </h2>
            
            {/* Subtitle */}
            <p className="text-base font-ibm-condensed font-extralight text-[#737373] mb-8 leading-relaxed">
              Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.
            </p>

            {/* File Upload Area */}
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center mb-6 transition-colors ${
                file ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
            >
              {file ? (
                <div className="space-y-3">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
                  <p className="font-ibm-condensed font-extralight text-sm text-gray-600">
                    {file.name}
                  </p>
                  <button
                    onClick={() => setFile(null)}
                    className="text-red-500 hover:text-red-700 font-ibm-condensed font-extralight text-sm"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                  <p className="font-ibm-condensed font-extralight text-sm text-gray-600">
                    Drag & drop your resume here
                  </p>
                  <p className="font-ibm-condensed font-extralight text-xs text-gray-500">
                    or click to browse
                  </p>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer inline-block px-4 py-2 bg-blue-600 text-white rounded-lg font-ibm-condensed font-extralight text-sm hover:bg-blue-700 transition-colors"
                  >
                    Browse Files
                  </label>
                </div>
              )}
            </div>

            {/* Job Description Input */}
            <div className="mb-6">
              <label className="block font-ibm-condensed font-extralight text-sm font-medium text-gray-700 mb-2">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg resize-none font-ibm-condensed font-extralight text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Analyze Button */}
            <button
              onClick={analyzeResume}
              disabled={!file || !jobDescription.trim() || isAnalyzing}
              className={`w-full py-3 px-6 rounded-lg font-ibm-condensed font-extralight text-sm font-medium transition-all ${
                !file || !jobDescription.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin inline mr-2" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 inline mr-2" />
                  Analyze Resume
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Panel - Results Section */}
        <div className="w-full lg:w-1/2 bg-white p-8 overflow-y-auto">
          <div className="max-w-2xl mx-auto">
            {!results ? (
              /* Empty State */
              <div className="text-center py-20">
                <BarChart3 className="h-24 w-24 text-gray-300 mx-auto mb-6" />
                <h3 className="text-2xl font-ibm-condensed font-extralight text-gray-400 mb-4">
                  Ready to analyze your resume?
                </h3>
                <p className="font-ibm-condensed font-extralight text-gray-500">
                  Upload your resume and paste a job description to get started.
                </p>
              </div>
            ) : results.error ? (
              /* Error State */
              <div className="text-center py-20">
                <AlertCircle className="h-24 w-24 text-red-300 mx-auto mb-6" />
                <h3 className="text-2xl font-ibm-condensed font-extralight text-red-600 mb-4">
                  Analysis Failed
                </h3>
                <p className="font-ibm-condensed font-extralight text-red-500">
                  {results.error}
                </p>
              </div>
            ) : (
              /* Results Display */
              <div className="space-y-6">
                <h3 className="text-2xl font-ibm-condensed font-extralight text-gray-800 mb-6">
                  Analysis Results
                </h3>
                
                {/* ATS Score */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800">
                      ATS Match Score
                    </h4>
                    <span className="text-3xl font-ibm-condensed font-extralight text-blue-600">
                      {results.ats_score}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${results.ats_score}%` }}
                    />
                  </div>
                </div>

                {/* Keywords Found */}
                <div className="bg-green-50 p-6 rounded-xl border border-green-200">
                  <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800 mb-4">
                    Keywords Found
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {results.keywords_found?.map((keyword: string, index: number) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-ibm-condensed font-extralight text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Missing Keywords */}
                <div className="bg-red-50 p-6 rounded-xl border border-red-200">
                  <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800 mb-4">
                    Missing Keywords
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {results.keywords_missing?.map((keyword: string, index: number) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-ibm-condensed font-extralight text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>

                {/* File Info */}
                <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
                  <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800 mb-4">
                    File Information
                  </h4>
                  <div className="space-y-2 font-ibm-condensed font-extralight text-sm text-gray-600">
                    <p><strong>Filename:</strong> {results.file_info?.filename}</p>
                    <p><strong>Size:</strong> {(results.file_info?.size / 1024).toFixed(1)} KB</p>
                    <p><strong>Type:</strong> {results.file_info?.content_type}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Debug Info */}
      {debugInfo && (
        <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg max-w-md font-ibm-condensed font-extralight text-sm">
          <div className="font-bold mb-2">Debug Info:</div>
          <div className="whitespace-pre-wrap">{debugInfo}</div>
        </div>
      )}
    </div>
  );
}
