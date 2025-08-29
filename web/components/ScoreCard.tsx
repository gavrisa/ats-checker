'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Target, BarChart3 } from 'lucide-react';

interface ScoreCardProps {
  score: number;
  textSimilarity: number;
  keywordCoverage: number;
}

export default function ScoreCard({ score, textSimilarity, keywordCoverage }: ScoreCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Needs Work';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    if (score >= 40) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="card p-8 text-center"
    >
      <motion.div
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-6"
      >
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your ATS Match Score</h2>
        <p className="text-gray-600">How well your resume matches the job description</p>
      </motion.div>

      {/* Main Score */}
      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4, type: "spring", stiffness: 200 }}
        className={`inline-flex items-center justify-center w-32 h-32 rounded-full mx-auto mb-6 ${getScoreBg(score)} border-4`}
      >
        <div className="text-center">
          <div className={`text-4xl font-bold ${getScoreColor(score)}`}>
            {score}
          </div>
          <div className="text-sm font-medium text-gray-600">/100</div>
        </div>
      </motion.div>

      {/* Score Label */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        className="mb-8"
      >
        <h3 className={`text-xl font-semibold ${getScoreColor(score)} mb-2`}>
          {getScoreLabel(score)}
        </h3>
        <p className="text-gray-600">
          {score >= 80 ? "🎉 Your resume is highly compatible with this job!" :
           score >= 60 ? "👍 Good compatibility, some improvements possible" :
           score >= 40 ? "⚠️ Moderate compatibility, several areas to improve" :
           "❌ Low compatibility, significant improvements needed"}
        </p>
      </motion.div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Text Similarity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 1.0 }}
          className="card p-6 bg-blue-50 border-blue-200"
        >
          <div className="flex items-center gap-3 mb-3">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h4 className="font-semibold text-gray-900">Text Similarity</h4>
          </div>
          <div className="text-3xl font-bold text-blue-600 mb-3">
            {textSimilarity}%
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2 mb-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${textSimilarity}%` }}
              transition={{ duration: 1, delay: 1.2 }}
              className="bg-blue-600 h-2 rounded-full"
            />
          </div>
          <p className="text-sm text-blue-700">
            How similar your resume text is to the job description
          </p>
        </motion.div>

        {/* Keyword Coverage */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 1.1 }}
          className="card p-6 bg-green-50 border-green-200"
        >
          <div className="flex items-center gap-3 mb-3">
            <Target className="w-5 h-5 text-green-600" />
            <h4 className="font-semibold text-gray-900">Keyword Coverage</h4>
          </div>
          <div className="text-3xl font-bold text-green-600 mb-3">
            {keywordCoverage}%
          </div>
          <div className="w-full bg-green-200 rounded-full h-2 mb-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${keywordCoverage}%` }}
              transition={{ duration: 1, delay: 1.3 }}
              className="bg-green-600 h-2 rounded-full"
            />
          </div>
          <p className="text-sm text-green-700">
            Percentage of job keywords found in your resume
          </p>
        </motion.div>
      </div>

      {/* Overall Progress Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        className="mt-8"
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-medium text-gray-700">{score}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${score}%` }}
            transition={{ duration: 1.5, delay: 1.5, ease: "easeOut" }}
            className={`h-3 rounded-full ${
              score >= 80 ? 'bg-green-500' :
              score >= 60 ? 'bg-yellow-500' :
              score >= 40 ? 'bg-orange-500' :
              'bg-red-500'
            }`}
          />
        </div>
      </motion.div>
    </motion.div>
  );
}
