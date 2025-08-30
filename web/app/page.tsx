'use client';

import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !jobDescription) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('resume_file', file);
    formData.append('job_description', jobDescription);

    try {
      const response = await fetch('https://ats-checker-r82q.onrender.com/analyze', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        setResult({ error: 'Analysis failed' });
      }
    } catch (error) {
      setResult({ error: 'Network error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-gray-900 mb-8">
          ATS Resume Checker
        </h1>
        
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
