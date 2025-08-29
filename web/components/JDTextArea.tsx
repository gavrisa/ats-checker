'use client';

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { FileText, AlertCircle } from 'lucide-react';

interface JDTextAreaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minLength?: number;
  maxLength?: number;
}

export default function JDTextArea({
  value,
  onChange,
  placeholder = "Paste the job description here...",
  minLength = 50,
  maxLength = 5000
}: JDTextAreaProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [charCount, setCharCount] = useState(0);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setCharCount(newValue.length);
    onChange(newValue);
  }, [onChange]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  const isValid = charCount >= minLength;
  const isTooLong = charCount > maxLength;

  const getStatusColor = () => {
    if (isTooLong) return 'text-red-500';
    if (isValid) return 'text-green-500';
    return 'text-gray-400';
  };

  const getStatusIcon = () => {
    if (isTooLong) return <AlertCircle className="w-4 h-4 text-red-500" />;
    if (isValid) return <FileText className="w-4 h-4 text-green-500" />;
    return <FileText className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Job Description
        </h3>
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {charCount}/{maxLength}
          </span>
        </div>
      </div>

      <motion.div
        animate={{
          borderColor: isFocused ? 'hsl(var(--ring))' : 'hsl(var(--border))',
          boxShadow: isFocused ? '0 0 0 2px hsl(var(--ring))' : 'none'
        }}
        transition={{ duration: 0.2 }}
        className="relative"
      >
        <textarea
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          className="textarea w-full min-h-[200px] resize-none"
          maxLength={maxLength}
        />
        
        {isFocused && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute -bottom-8 left-0 text-xs text-gray-500"
          >
            {isValid ? (
              <span className="text-green-600">✓ Ready to analyze</span>
            ) : (
              <span className="text-gray-500">
                Need at least {minLength} characters ({minLength - charCount} more)
              </span>
            )}
          </motion.div>
        )}
      </motion.div>

      {isTooLong && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg"
        >
          <p className="text-sm text-red-600">
            Job description is too long. Please keep it under {maxLength} characters.
          </p>
        </motion.div>
      )}

      <div className="mt-3 text-xs text-gray-500">
        <p>• Minimum {minLength} characters required for analysis</p>
        <p>• Maximum {maxLength} characters allowed</p>
        <p>• Copy and paste the complete job description</p>
      </div>
    </div>
  );
}
