'use client';

import { useState } from 'react';
import { Upload, Search, FileText, CheckCircle, AlertCircle, RefreshCw, BarChart3 } from 'lucide-react';
import { config } from '../config';

// Force Vercel to detect changes and deploy latest updates
// Latest commit: Font cleanup, IBM Plex only, perfect button specs
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
            className={`px-4 py-2 rounded-lg font-ibm-condensed font-extralight text-sm transition-colors active:outline-none active:ring-0 active:border-0 ${
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

      {/* Main Content - Responsive Layout */}
      <div className="flex flex-col lg:flex-row h-screen">
        {/* Left Panel - Input Section */}
        <div className="w-full lg:w-1/2 bg-[#F2F2F2] overflow-hidden flex flex-col">
          {/* Content Area - Exact CSS specifications */}
          <div 
            className="flex-1 px-[90px]"
            style={{
              display: 'flex',
              width: '896px',
              height: '900px',
              paddingTop: '80px',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: '48px',
              flexShrink: 0
            }}
          >
            {/* Text Block - Header + Description - Width 571px, spacing 4px */}
            <div className="w-[571px] space-y-1">
              {/* Main Heading - 48px #000000 */}
              <h2 className="text-[48px] font-ibm-condensed font-extralight text-black leading-tight">
                Is your resume ATS-ready?
              </h2>
              
              {/* Description - 16px #575656 */}
              <p className="text-[16px] font-ibm-condensed font-extralight text-[#575656] leading-relaxed">
                Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.
              </p>
            </div>
            


            {/* Upload File Component */}
            <div className="w-[571px]">
              {/* Title: "Upload Resume" 16px #000000 */}
              <h3 className="text-[16px] font-ibm-condensed font-extralight text-black mb-3">
                Upload Resume
              </h3>
              
              {/* Spacing 12px */}
              <div className="h-3"></div>
              
              {/* Upload Field - height 64px, width fill content block, border #000000, radius 4px */}
              <div
                className={`h-16 w-full border border-black rounded transition-colors ${
                  file ? 'border-blue-500 bg-blue-50' : 'border-black hover:border-gray-600'
                }`}
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
              >
                {file ? (
                  <div className="h-full flex items-center justify-center space-x-4">
                    <CheckCircle className="h-6 w-6 text-green-500" />
                    <p className="text-[16px] font-ibm-condensed font-extralight text-black">
                      {file.name}
                    </p>
                    <button
                      onClick={() => setFile(null)}
                      className="text-red-500 hover:text-red-700 font-ibm-condensed font-extralight text-[16px] active:outline-none active:ring-0 active:border-0"
                    >
                      Remove File
                    </button>
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center space-x-4">
                    {/* Icon "resume" + text "drag and drop file here" spacing 16px */}
                    <div className="flex items-center space-x-4">
                      <div className="w-6 h-6 bg-black rounded"></div>
                      <p className="text-[16px] font-ibm-condensed font-extralight text-black">
                        drag and drop file here
                      </p>
                    </div>
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                    />
                    {/* Button browse - radius 2px, bg #000000 text #ffffff height 36px width 96px */}
                    <label
                      htmlFor="file-upload"
                      className="cursor-pointer inline-flex items-center justify-center h-9 w-24 bg-black text-white rounded-sm font-ibm-condensed font-extralight text-[16px] hover:bg-gray-800 active:outline-none active:ring-0 active:border-0 transition-colors"
                    >
                      Browse
                    </label>
                  </div>
                )}
              </div>
              
              {/* Spacing 8px */}
              <div className="h-2"></div>
              
              {/* Description: "Limit 200MB per file. Supported file types: PDF, DOC, DOCX" 12px #737373 */}
              <p className="text-[12px] font-ibm-condensed font-extralight text-[#737373]">
                Limit 200MB per file. Supported file types: PDF, DOC, DOCX
              </p>
            </div>
            


            {/* Text Field Component */}
            <div className="w-[571px]">
              {/* Title "Job Description" 16px #000000 */}
              <label className="block font-ibm-condensed font-extralight text-[16px] text-black mb-3">
                Job Description
              </label>
              
              {/* Spacing 12px */}
              <div className="h-3"></div>
              
              {/* Text field - width fill content block, height fill content block but so content block and buttons should be spacing 48px */}
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                className="w-full border border-black rounded-md resize-none font-ibm-condensed font-extralight text-[12px] text-[#737373] focus:outline-none focus:ring-0 focus:border-black transition-colors"
                style={{ 
                  height: '200px', // Fixed height to ensure proper spacing
                  padding: '16px'
                }}
              />
            </div>
            

          </div>

          {/* Action Buttons - Maintain 48px spacing with content above */}
          <div className="px-[90px] flex-shrink-0">
            <div className="flex flex-col sm:flex-row gap-0">
              {/* Start Over Button - Secondary Button - NO STROKE ON ACTIVE */}
              <button
                onClick={() => {
                  setFile(null);
                  setJobDescription('');
                  setResults(null);
                }}
                className="hidden sm:block flex-1 h-16 sm:h-[72px] lg:h-[80px] px-6 font-ibm-condensed font-extralight text-base border-0 text-black bg-[#ebebeb] hover:bg-[#f8f8f8] focus:bg-[#ebebeb] focus:outline-none focus:ring-0 focus:ring-offset-0 active:bg-[#ebebeb] active:outline-none active:ring-0 active:border-0 transition-all flex items-center justify-center"
              >
                Start Over
              </button>
              
              {/* Get My Score Button - Primary Button - IBM Extra Light 200 */}
              <button
                onClick={analyzeResume}
                className="flex-1 h-16 sm:h-[72px] lg:h-[80px] px-6 font-ibm-condensed font-extralight text-base border-0 bg-black text-white hover:bg-[#2f2f2f] active:bg-black active:outline-none active:ring-0 active:border-0 transition-all flex items-center justify-center"
              >
                {isAnalyzing ? (
                  <>
                    Analyzing...
                  </>
                ) : (
                  <>
                    Get My Score
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel - Results Section */}
        <div className="w-full lg:w-1/2 bg-white p-6 sm:p-8 lg:p-8 xl:p-8 2xl:p-8 overflow-y-auto">
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
