'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Upload, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  RefreshCw,
  Zap
} from 'lucide-react';

import FileUploader from '../components/FileUploader';
import JDTextArea from '../components/JDTextArea';
import ScoreCard from '../components/ScoreCard';
import KeywordChips from '../components/KeywordChips';
import BulletSuggestions from '../components/BulletSuggestions';

interface AnalysisResult {
  score: number;
  textSimilarity: number;
  keywordCoverage: number;
  jdKeywordsTop30: string[];
  present: string[];
  missing: string[];
  bullets: string[];
  analysis: {
    resumeWords: number;
    jdWords: number;
    keywordsFound: number;
    keywordsMissing: number;
    totalKeywords: number;
  };
}

export default function Home() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>('');

  const canAnalyze = resumeFile && jobDescription.trim().length >= 50;

  const analyzeResume = async () => {
    if (!canAnalyze) return;

    setIsAnalyzing(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('resume_file', resumeFile);
      formData.append('job_description', jobDescription);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const startOver = () => {
    setResumeFile(null);
    setJobDescription('');
    setAnalysisResult(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              ATS Resume Checker
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Check how your resume matches any job description. Get missing keywords, 
              smart bullets, and a clear path to 100% coverage.
            </p>
          </motion.div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Inputs */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="lg:col-span-1 space-y-6"
          >
            {/* Resume Upload */}
            <div className="card p-6">
              <FileUploader
                onFileSelect={setResumeFile}
                acceptedTypes={['.pdf', '.docx', '.doc', '.txt']}
                maxSize={10}
              />
            </div>

            {/* Job Description */}
            <div className="card p-6">
              <JDTextArea
                value={jobDescription}
                onChange={setJobDescription}
                minLength={50}
                maxLength={5000}
              />
            </div>

            {/* Action Buttons */}
            <div className="card p-6">
              <div className="space-y-3">
                <button
                  onClick={analyzeResume}
                  disabled={!canAnalyze || isAnalyzing}
                  className="btn btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      Check My Match
                    </>
                  )}
                </button>

                <button
                  onClick={startOver}
                  className="btn btn-outline w-full flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Start Over
                </button>
              </div>

              {/* Status Indicators */}
              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  {resumeFile ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-gray-400" />
                  )}
                  <span className={resumeFile ? 'text-green-600' : 'text-gray-500'}>
                    Resume uploaded
                  </span>
                </div>
                
                <div className="flex items-center gap-2 text-sm">
                  {jobDescription.trim().length >= 50 ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-gray-400" />
                  )}
                  <span className={jobDescription.trim().length >= 50 ? 'text-green-600' : 'text-gray-500'}>
                    Job description ready
                  </span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right Panel - Results */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="lg:col-span-2 space-y-6"
          >
            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="card p-6 bg-red-50 border-red-200"
                >
                  <div className="flex items-center gap-3">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                    <div>
                      <h3 className="font-semibold text-red-900">Analysis Error</h3>
                      <p className="text-red-700">{error}</p>
                    </div>
                  </div>
                </motion.div>
              )}

              {isAnalyzing && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="card p-12 text-center"
                >
                  <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Analyzing Your Resume
                  </h3>
                  <p className="text-gray-600">
                    Processing your resume and comparing it with the job description...
                  </p>
                </motion.div>
              )}

              {analysisResult && !isAnalyzing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-8"
                >
                  {/* Score Card */}
                  <ScoreCard
                    score={analysisResult.score}
                    textSimilarity={analysisResult.textSimilarity}
                    keywordCoverage={analysisResult.keywordCoverage}
                  />

                  {/* Keyword Analysis */}
                  <KeywordChips
                    jdKeywordsTop30={analysisResult.jdKeywordsTop30}
                    present={analysisResult.present}
                    missing={analysisResult.missing}
                  />

                  {/* Bullet Suggestions */}
                  <BulletSuggestions
                    bullets={analysisResult.bullets}
                    missingKeywords={analysisResult.missing}
                  />

                  {/* Analysis Summary */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 1.2 }}
                    className="card p-6 bg-gray-50 border-gray-200"
                  >
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
                      Analysis Summary
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-bold text-blue-600">
                          {analysisResult.analysis.resumeWords}
                        </div>
                        <div className="text-sm text-gray-600">Resume Words</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-green-600">
                          {analysisResult.analysis.jdWords}
                        </div>
                        <div className="text-sm text-gray-600">JD Words</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-purple-600">
                          {analysisResult.analysis.keywordsFound}
                        </div>
                        <div className="text-sm text-gray-600">Keywords Found</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-orange-600">
                          {analysisResult.analysis.keywordsMissing}
                        </div>
                        <div className="text-sm text-gray-600">Keywords Missing</div>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              )}

              {!analysisResult && !isAnalyzing && !error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="card p-12 text-center bg-gray-50 border-gray-200"
                >
                  <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    Ready to Analyze
                  </h3>
                  <p className="text-gray-600">
                    Upload your resume and paste a job description to get started.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-gray-600">
            <p>ATS Resume Checker - Built with Next.js and FastAPI</p>
            <p className="text-sm mt-2">
              Optimize your resume for Applicant Tracking Systems
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
