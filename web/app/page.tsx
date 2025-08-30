'use client';

import { useState } from 'react';
import { config } from '../config';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
      
      setDebugInfo(`Response status: ${response.status} ${response.statusText}`);
      
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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-gray-900 mb-8">
          ATS Resume Checker
        </h1>
        
        {/* Connection Test */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <strong>Backend URL:</strong> {config.backendUrl}
            </div>
            <button
              onClick={testConnection}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Test Connection
            </button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Resume
            </label>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full p-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Description
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              className="w-full p-3 border border-gray-300 rounded-md h-32"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze Resume'}
          </button>
        </form>

        {/* Debug Information */}
        {debugInfo && (
          <div className="bg-gray-100 border border-gray-300 rounded-lg p-4 mb-6">
            <h3 className="font-semibold mb-2">Debug Info:</h3>
            <pre className="text-sm text-gray-700 whitespace-pre-wrap">{debugInfo}</pre>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Analysis Results</h2>
            {result.error ? (
              <div className="text-red-600">{result.error}</div>
            ) : (
              <div className="space-y-4">
                <div>
                  <strong>ATS Score:</strong> {result.ats_score}/100
                </div>
                <div>
                  <strong>Keywords Found:</strong> {result.keywords_found?.join(', ')}
                </div>
                <div>
                  <strong>Keywords Missing:</strong> {result.keywords_missing?.join(', ')}
                </div>
                <div>
                  <strong>File:</strong> {result.file_info?.filename}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
