'use client';

import { useState } from 'react';
import { config } from '../config';
import { 
  FileText, 
  Upload, 
  Search, 
  CheckCircle, 
  AlertCircle, 
  FileIcon,
  RefreshCw,
  BarChart3
} from 'lucide-react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string>('');

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmit = async () => {
    if (!file || !jobDescription) return;

    setLoading(true);
    setDebugInfo('');
    const formData = new FormData();
    formData.append('resume_file', file);
    formData.append('job_description', jobDescription);

    try {
      const url = `${config.backendUrl}${config.endpoints.analyze}`;
      setDebugInfo(`Connecting to: ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setResult(data);
        setDebugInfo(`Success! Received data: ${JSON.stringify(data, null, 2)}`);
      } else {
        const errorText = await response.text();
        setResult({ error: `Analysis failed: ${response.status} ${response.statusText}` });
        setDebugInfo(`Error response: ${errorText}`);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setResult({ error: `Network error: ${errorMessage}` });
      setDebugInfo(`Exception: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const startOver = () => {
    setFile(null);
    setJobDescription('');
    setResult(null);
    setDebugInfo('');
  };

  const testConnection = async () => {
    try {
      setDebugInfo('Testing connection to backend...');
      const response = await fetch(`${config.backendUrl}${config.endpoints.health}`);
      if (response.ok) {
        const data = await response.json();
        setDebugInfo(`✅ Backend connected! Health: ${JSON.stringify(data)}`);
      } else {
        setDebugInfo(`❌ Backend health check failed: ${response.status}`);
      }
    } catch (error) {
      setDebugInfo(`❌ Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Section - Input and Instructions - Fixed height, non-scrollable */}
      <div className="w-1/2 bg-[#F2F2F2] p-6 lg:p-8 flex flex-col h-screen overflow-hidden">
        <div className="mb-6 lg:mb-8 flex-shrink-0">
          <h1 className="text-2xl lg:text-4xl font-display font-bold text-gray-800 mb-3 lg:mb-4 leading-tight">
            Is your resume ATS-ready?
          </h1>
          <p className="text-sm lg:text-lg font-body text-gray-600 leading-relaxed">
            Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.
          </p>
        </div>

        {/* Upload Resume Area - Fixed size */}
        <div className="mb-6 lg:mb-8 flex-shrink-0">
          <h2 className="text-lg lg:text-xl font-display font-semibold text-gray-800 mb-3 lg:mb-4 flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Resume
          </h2>
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 lg:p-8 text-center hover:border-gray-400 transition-colors"
            onDrop={handleFileDrop}
            onDragOver={(e) => e.preventDefault()}
          >
            <div className="text-gray-400 mb-3 lg:mb-4">
              <FileText className="mx-auto h-8 w-8 lg:h-12 lg:w-12" />
            </div>
            <p className="text-sm lg:text-base font-body text-gray-600 mb-2">Drag and drop file here</p>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileSelect}
              className="hidden"
              id="file-input"
            />
            <label
              htmlFor="file-input"
              className="inline-block bg-gray-800 text-white px-4 lg:px-6 py-2 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors text-sm lg:text-base font-body"
            >
              Browse
            </label>
            {file && (
              <p className="text-xs lg:text-sm text-gray-500 mt-2 font-body flex items-center justify-center gap-2">
                <FileIcon className="h-4 w-4" />
                Selected: {file.name}
              </p>
            )}
          </div>
          <p className="text-xs lg:text-sm text-gray-500 mt-2 font-body">
            Limit 200MB per file. Supported file types: PDF, DOC, DOCX
          </p>
        </div>

        {/* Job Description Area - Flexible height, fills remaining space */}
        <div className="flex-1 min-h-0 mb-6 lg:mb-8">
          <h2 className="text-lg lg:text-xl font-display font-semibold text-gray-800 mb-3 lg:mb-4 flex items-center gap-2">
            <Search className="h-5 w-5" />
            Paste Job Description here
          </h2>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here..."
            className="w-full h-full min-h-[120px] lg:min-h-[160px] p-3 lg:p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent text-sm lg:text-base font-body"
          />
        </div>

        {/* Bottom Action Bar - Fixed at bottom */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-200 flex-shrink-0">
          <button
            onClick={startOver}
            className="text-gray-600 hover:text-gray-800 transition-colors text-sm lg:text-base font-body flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Start Over
          </button>
          <button
            onClick={handleSubmit}
            disabled={!file || !jobDescription || loading}
            className="bg-gray-800 text-white px-6 lg:px-8 py-2 lg:py-3 rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm lg:text-base font-body flex items-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <BarChart3 className="h-4 w-4" />
                Get My Score
              </>
            )}
          </button>
        </div>

        {/* Debug Info (Hidden by default, can be toggled) */}
        {debugInfo && (
          <div className="mt-4 p-3 lg:p-4 bg-gray-100 rounded-lg flex-shrink-0">
            <details className="text-xs lg:text-sm font-body">
              <summary className="cursor-pointer text-gray-600">Debug Info</summary>
              <pre className="mt-2 text-xs text-gray-700 whitespace-pre-wrap font-mono">{debugInfo}</pre>
            </details>
          </div>
        )}
      </div>

      {/* Right Section - Results Area - Scrollable */}
      <div className="w-1/2 bg-white p-6 lg:p-8 overflow-y-auto">
        {!result ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-gray-400">
              <FileText className="mx-auto h-12 w-12 lg:h-16 lg:w-16 mb-4" />
              <p className="text-base lg:text-lg font-body">Upload a resume and paste a job description to get started</p>
            </div>
          </div>
        ) : (
          <div className="h-full">
            <h2 className="text-xl lg:text-2xl font-display font-bold text-gray-800 mb-4 lg:mb-6">Your ATS Analysis Results</h2>
            
            {result.error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 lg:p-6">
                <div className="text-red-800">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5" />
                    Analysis Failed
                  </h3>
                  <p className="font-body">{result.error}</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4 lg:space-y-6">
                {/* ATS Score */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 lg:p-6">
                  <h3 className="text-base lg:text-lg font-display font-semibold text-blue-800 mb-2 flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    ATS Score
                  </h3>
                  <div className="text-2xl lg:text-3xl font-display font-bold text-blue-600">{result.ats_score}/100</div>
                </div>

                {/* Keywords Found */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 lg:p-6">
                  <h3 className="text-base lg:text-lg font-display font-semibold text-green-800 mb-3 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5" />
                    Keywords Found
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {result.keywords_found?.map((keyword: string, index: number) => (
                      <span key={index} className="bg-green-200 text-green-800 px-2 lg:px-3 py-1 rounded-full text-xs lg:text-sm font-body">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Keywords Missing */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 lg:p-6">
                  <h3 className="text-base lg:text-lg font-display font-semibold text-yellow-800 mb-3 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5" />
                    Keywords Missing
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {result.keywords_missing?.map((keyword: string, index: number) => (
                      <span key={index} className="bg-yellow-200 text-yellow-800 px-2 lg:px-3 py-1 rounded-full text-xs lg:text-sm font-body">
                        {keyword}
                      </span>
                ))}
                  </div>
                </div>

                {/* File Info */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 lg:p-6">
                  <h3 className="text-base lg:text-lg font-display font-semibold text-gray-800 mb-2 flex items-center gap-2">
                    <FileIcon className="h-5 w-5" />
                    File Information
                  </h3>
                  <p className="text-gray-600 text-sm lg:text-base font-body">Filename: {result.file_info?.filename}</p>
                  <p className="text-gray-600 text-sm lg:text-base font-body">Size: {(result.file_info?.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
