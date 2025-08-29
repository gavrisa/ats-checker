'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Target, AlertTriangle } from 'lucide-react';

interface KeywordChipsProps {
  jdKeywordsTop30: string[];
  present: string[];
  missing: string[];
}

export default function KeywordChips({ jdKeywordsTop30, present, missing }: KeywordChipsProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.8 },
    visible: { opacity: 1, y: 0, scale: 1 }
  };

  const chipVariants = {
    hover: { scale: 1.05, y: -2 },
    tap: { scale: 0.95 }
  };

  return (
    <div className="space-y-8">
      {/* All Keywords Section */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="card p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">All JD Keywords (Top 30)</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          <AnimatePresence>
            {jdKeywordsTop30.map((keyword, index) => (
              <motion.span
                key={keyword}
                variants={itemVariants}
                whileHover="hover"
                whileTap="tap"
                variants={chipVariants}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium border border-gray-200"
              >
                {keyword}
              </motion.span>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Present vs Missing Keywords */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Present Keywords */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="card p-6 bg-green-50 border-green-200"
        >
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold text-green-900">Present in your resume</h3>
          </div>
          
          {present.length > 0 ? (
            <div className="flex flex-wrap gap-2 mb-3">
              <AnimatePresence>
                {present.map((keyword, index) => (
                  <motion.span
                    key={keyword}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    whileHover={{ scale: 1.05 }}
                    className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium border border-green-300"
                  >
                    {keyword}
                  </motion.span>
                ))}
              </AnimatePresence>
            </div>
          ) : (
            <div className="text-center py-4">
              <AlertTriangle className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <p className="text-green-600 text-sm">No keywords found</p>
            </div>
          )}
          
          <div className="text-sm text-green-700">
            <p className="font-medium">Great job! You're covering {present.length} out of {jdKeywordsTop30.length} top JD keywords</p>
            <p className="text-xs mt-1 opacity-75">
              These keywords help ATS systems recognize your resume as relevant
            </p>
          </div>
        </motion.div>

        {/* Missing Keywords */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="card p-6 bg-red-50 border-red-200"
        >
          <div className="flex items-center gap-2 mb-4">
            <XCircle className="w-5 h-5 text-red-600" />
            <h3 className="text-lg font-semibold text-red-900">Missing / low-visibility keywords</h3>
          </div>
          
          {missing.length > 0 ? (
            <div className="flex flex-wrap gap-2 mb-3">
              <AnimatePresence>
                {missing.slice(0, 10).map((keyword, index) => (
                  <motion.span
                    key={keyword}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    whileHover={{ scale: 1.05 }}
                    className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium border border-red-300"
                  >
                    {keyword}
                  </motion.span>
                ))}
              </AnimatePresence>
            </div>
          ) : (
            <div className="text-center py-4">
              <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <p className="text-green-600 text-sm">Perfect! All keywords covered</p>
            </div>
          )}
          
          <div className="text-sm text-red-700">
            <p className="font-medium">
              {missing.length > 0 
                ? `Showing top ${Math.min(10, missing.length)} most relevant missing keywords. Add these to improve your coverage.`
                : "Excellent keyword coverage!"
              }
            </p>
            <p className="text-xs mt-1 opacity-75">
              {missing.length > 0 
                ? "Including these keywords naturally in your resume will boost your ATS score"
                : "Your resume is well-optimized for this position"
              }
            </p>
          </div>
        </motion.div>
      </div>

      {/* Coverage Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="card p-6 bg-blue-50 border-blue-200"
      >
        <div className="text-center">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Keyword Coverage Summary</h3>
          <div className="flex items-center justify-center gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{present.length}</div>
              <div className="text-sm text-blue-700">Found</div>
            </div>
            <div className="text-2xl font-bold text-gray-400">/</div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{jdKeywordsTop30.length}</div>
              <div className="text-sm text-blue-700">Total</div>
            </div>
            <div className="text-2xl font-bold text-gray-400">=</div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round((present.length / jdKeywordsTop30.length) * 100)}%
              </div>
              <div className="text-sm text-blue-700">Coverage</div>
            </div>
          </div>
          
          <div className="w-full bg-blue-200 rounded-full h-3">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(present.length / jdKeywordsTop30.length) * 100}%` }}
              transition={{ duration: 1, delay: 0.8 }}
              className="bg-blue-600 h-3 rounded-full"
            />
          </div>
        </div>
      </motion.div>
    </div>
  );
}
