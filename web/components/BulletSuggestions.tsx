'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, Copy, CheckCircle, TrendingUp } from 'lucide-react';

interface BulletSuggestionsProps {
  bullets: string[];
  missingKeywords: string[];
}

export default function BulletSuggestions({ bullets, missingKeywords }: BulletSuggestionsProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const highlightKeywords = (text: string) => {
    if (!missingKeywords.length) return text;

    const parts = [];
    let lastIndex = 0;

    // Find and highlight missing keywords
    missingKeywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      let match;
      while ((match = regex.exec(text)) !== null) {
        // Add text before the keyword
        if (match.index > lastIndex) {
          parts.push(text.slice(lastIndex, match.index));
        }
        
        // Add highlighted keyword
        parts.push(
          <span key={`${keyword}-${match.index}`} className="font-semibold text-blue-600 bg-blue-100 px-1 rounded">
            {match[0]}
          </span>
        );
        
        lastIndex = match.index + match[0].length;
      }
    });

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: { opacity: 1, y: 0, scale: 1 }
  };

  if (!bullets.length) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="card p-8 text-center bg-gray-50 border-gray-200"
      >
        <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-700 mb-2">No Bullet Suggestions Available</h3>
        <p className="text-gray-600">
          Great job! Your resume already covers all the important keywords.
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-yellow-100 rounded-lg">
          <Lightbulb className="w-6 h-6 text-yellow-600" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Bullet Suggestions</h3>
          <p className="text-gray-600">Smart bullet points to add to your resume</p>
        </div>
      </div>

      {/* Bullets Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AnimatePresence>
          {bullets.map((bullet, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ y: -2, scale: 1.02 }}
              className="card p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover:shadow-lg transition-all duration-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium text-blue-700">Suggestion {index + 1}</span>
                </div>
                <button
                  onClick={() => copyToClipboard(bullet, index)}
                  className="p-2 hover:bg-blue-100 rounded-lg transition-colors group"
                  title="Copy to clipboard"
                >
                  {copiedIndex === index ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4 text-blue-600 group-hover:text-blue-700" />
                  )}
                </button>
              </div>

              <div className="mb-4">
                <p className="text-gray-800 leading-relaxed">
                  {highlightKeywords(bullet)}
                </p>
              </div>

              <div className="flex items-center gap-2 text-xs text-blue-600">
                <TrendingUp className="w-3 h-3" />
                <span>Click copy button to use this bullet</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Tips Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="card p-6 bg-yellow-50 border-yellow-200"
      >
        <div className="flex items-start gap-3">
          <Lightbulb className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 className="font-semibold text-yellow-900 mb-2">💡 Pro Tips</h4>
            <ul className="text-sm text-yellow-800 space-y-1">
              <li>• Customize these bullets with your specific metrics and achievements</li>
              <li>• Integrate keywords naturally into your existing bullet points</li>
              <li>• Focus on quantifiable results and measurable impact</li>
              <li>• Use action verbs and industry-specific terminology</li>
              <li>• Ensure bullets align with the job requirements and company culture</li>
            </ul>
          </div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1.0 }}
        className="flex flex-col sm:flex-row gap-3 justify-center"
      >
        <button
          onClick={() => {
            const allBullets = bullets.join('\n\n');
            copyToClipboard(allBullets, -1);
          }}
          className="btn btn-primary flex items-center gap-2"
        >
          <Copy className="w-4 h-4" />
          Copy All Suggestions
        </button>
        
        <button
          onClick={() => window.open('https://resumegenius.com/blog/resume-help/resume-bullet-points', '_blank')}
          className="btn btn-outline flex items-center gap-2"
        >
          <TrendingUp className="w-4 h-4" />
          Learn More About Bullet Points
        </button>
      </motion.div>
    </motion.div>
  );
}
