'use client';

import { useState, useEffect, useRef } from 'react';
import { Upload, Search, AlertCircle, BarChart3 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { config } from '../config';
import KeywordCoverage from '../components/KeywordCoverage';

// Force Vercel to detect changes and deploy latest updates
// Latest commit: Custom icons added, syntax errors fixed, ready for deployment
// Vercel deployment trigger - significant change to force rebuild

type UploadStatus = 'idle' | 'uploading' | 'uploaded' | 'failed';
export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [fieldErrors, setFieldErrors] = useState<{
    resume?: string;
    jobDescription?: string;
  }>({});
  const [animatedScore, setAnimatedScore] = useState<number>(0);
  const [previousScore, setPreviousScore] = useState<number>(0);
  
  // Animated metrics state
  const [animatedTextSimilarity, setAnimatedTextSimilarity] = useState<number>(0);
  const [previousTextSimilarity, setPreviousTextSimilarity] = useState<number>(0);
  const [animatedKeywordCoverage, setAnimatedKeywordCoverage] = useState<number>(0);
  const [previousKeywordCoverage, setPreviousKeywordCoverage] = useState<number>(0);
  const [animatedKeywordCount, setAnimatedKeywordCount] = useState<number>(0);
  const [previousKeywordCount, setPreviousKeywordCount] = useState<number>(0);
  
  // Animated progress bar state
  const [animatedAtsBarWidth, setAnimatedAtsBarWidth] = useState<number>(0);
  const [animatedKeywordCoverageBarWidth, setAnimatedKeywordCoverageBarWidth] = useState<number>(0);
  
  // Animation cleanup refs
  const animationTimeoutsRef = useRef<NodeJS.Timeout[]>([]);
  const animationFramesRef = useRef<number[]>([]);
  const lastResultsRef = useRef<any>(null);
  const isNewResultsRef = useRef<boolean>(false);
  const [animationRunId, setAnimationRunId] = useState<number>(0);



  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [screenWidth, setScreenWidth] = useState(0);





  // Highlight missing keywords in bullet suggestions
  const highlightKeywords = (text: string, keywords: string[]) => {
    if (!keywords || keywords.length === 0) return text;
    
    // Sort keywords by length (longest first) to avoid partial matches
    const sortedKeywords = [...keywords].sort((a, b) => b.length - a.length);
    
    let highlightedText = text;
    
    sortedKeywords.forEach(keyword => {
      // Create case-insensitive regex for the keyword
      const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
      
      // Replace keyword with styled span
      highlightedText = highlightedText.replace(regex, (match) => {
        return `<span style="font-weight: 500; color: #1f2937;">${match}</span>`;
      });
    });
    
    return highlightedText;
  };

  // Handle window resize for responsive layout
  useEffect(() => {
    const handleResize = () => {
      setScreenWidth(window.innerWidth);
    };
    
    // Set initial width
    handleResize();
    
    // Add event listener
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Cleanup function to stop all running animations
  const cleanupAnimations = () => {
    // Clear all timeouts
    animationTimeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    animationTimeoutsRef.current = [];
    
    // Cancel all animation frames
    animationFramesRef.current.forEach(frame => cancelAnimationFrame(frame));
    animationFramesRef.current = [];
  };

  // Validate and sanitize numeric values
  const validateNumericValue = (value: any, min: number = 0, max: number = 100): number => {
    if (typeof value !== 'number' || isNaN(value) || !isFinite(value)) {
      return min;
    }
    return Math.max(min, Math.min(max, value));
  };

  // Reusable animation function with proper cleanup
  const animateValue = (
    startValue: number,
    targetValue: number,
    duration: number,
    setter: (value: number) => void,
    onComplete?: () => void,
    useIntegers: boolean = false
  ) => {
    // Validate inputs
    const validStartValue = validateNumericValue(startValue);
    const validTargetValue = validateNumericValue(targetValue);
    
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (prefersReducedMotion) {
      setter(validTargetValue);
      onComplete?.();
      return;
    }
    
    const startTime = performance.now();
    let animationId: number;
    let lastDisplayedValue = validStartValue;
    
    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Ease-out cubic-bezier(0.22, 1, 0.36, 1)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      let currentValue = validStartValue + (validTargetValue - validStartValue) * easeOut;
      
      // Round to integers if requested (for ATS score)
      if (useIntegers) {
        currentValue = Math.round(currentValue);
      }
      
      // Only update if the value has meaningfully changed to reduce micro-flicker
      if (useIntegers) {
        // For integers, only update when the rounded value changes
        const roundedValue = Math.round(currentValue);
        if (roundedValue !== lastDisplayedValue) {
          setter(roundedValue);
          lastDisplayedValue = roundedValue;
        }
      } else {
        // For decimals, update more frequently but still reduce micro-flicker
        const roundedValue = Math.round(currentValue * 10) / 10; // One decimal place
        if (Math.abs(roundedValue - lastDisplayedValue) >= 0.1) {
          setter(roundedValue);
          lastDisplayedValue = roundedValue;
        }
      }
      
      if (progress < 1) {
        animationId = requestAnimationFrame(animate);
        animationFramesRef.current.push(animationId);
      } else {
        setter(validTargetValue);
        onComplete?.();
      }
    };
    
    animationId = requestAnimationFrame(animate);
    animationFramesRef.current.push(animationId);
  };

  // Animate all metrics when results change or animation is triggered
  useEffect(() => {
    // Always run animations when animationRunId changes (new click)
    // or when results change (new data)
    
    // Check if this is completely new results (different from previous)
    const isCompletelyNewResults = lastResultsRef.current !== null && 
      (lastResultsRef.current.score !== results?.score || 
       lastResultsRef.current.textSimilarity !== results?.textSimilarity ||
       lastResultsRef.current.keywordCoverage !== results?.keywordCoverage);
    
    lastResultsRef.current = results;
    isNewResultsRef.current = isCompletelyNewResults;
    
    // Cleanup any existing animations first
    cleanupAnimations();
    
    if (results && !results.error) {
      // Always start from 0 for animation replay (regardless of new/same results)
      const startScore = 0;
      const startSimilarity = 0;
      const startCoverage = 0;
      const startCount = 0;
      
      // All animations start simultaneously (synchronized)
      const targetScore = validateNumericValue(results.score, 0, 100);
      const targetSimilarity = validateNumericValue(results.textSimilarity, 0, 100);
      const targetCoverage = validateNumericValue(results.keywordCoverage, 0, 100);
      const totalKeywords = results.all_keywords ? results.all_keywords.length : 0;
      const matchedKeywords = results.matched_keywords ? results.matched_keywords.length : 0;
      const targetCount = validateNumericValue(matchedKeywords, 0, totalKeywords);
      // Start all animations at the same time with same duration (750ms)
      const timeout1 = setTimeout(() => {
        // ATS Score Animation (750ms) - use integers only
        animateValue(startScore, targetScore, 750, setAnimatedScore, () => {
          setPreviousScore(targetScore);
        }, true); // Use integers for ATS score
        
        // ATS Progress Bar Animation (750ms) - synchronized
        animateValue(0, targetScore, 750, setAnimatedAtsBarWidth, undefined, true);
        
        // Text Similarity Animation (750ms) - synchronized
        animateValue(startSimilarity, targetSimilarity, 750, setAnimatedTextSimilarity, () => {
          setPreviousTextSimilarity(targetSimilarity);
        });
        
        // Keyword Coverage Animation (750ms) - synchronized
        animateValue(startCoverage, targetCoverage, 750, setAnimatedKeywordCoverage, () => {
          setPreviousKeywordCoverage(targetCoverage);
        });
        
        // Keyword Coverage Progress Bar Animation (750ms) - synchronized
        animateValue(0, targetCoverage, 750, setAnimatedKeywordCoverageBarWidth);
        
        // Keyword Count Animation (750ms) - synchronized
        animateValue(startCount, targetCount, 750, setAnimatedKeywordCount, () => {
          setPreviousKeywordCount(targetCount);
        });
      }, 50); // Small delay to ensure cleanup is complete
      animationTimeoutsRef.current.push(timeout1);
    }
    
    // Cleanup function
    return () => {
      cleanupAnimations();
    };
  }, [results, animationRunId]);

  // Cleanup animations on component unmount
  useEffect(() => {
    return () => {
      cleanupAnimations();
    };
  }, []);

  // Handle file drop
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      if (config.allowedFileTypes.some(type => droppedFile.name.toLowerCase().endsWith(type))) {
        setUploadStatus('uploading');
        setUploadProgress(0);
        
        // Simulate upload progress
        const interval = setInterval(() => {
          setUploadProgress(prev => {
            if (prev >= 100) {
              clearInterval(interval);
              setUploadStatus('uploaded');
              return 100;
            }
            return prev + 10;
          });
        }, 100);
        
        setFile(droppedFile);
        // Clear resume field error when file is selected
        if (fieldErrors.resume) {
          setFieldErrors(prev => ({ ...prev, resume: undefined }));
        }
      } else {
        // Unsupported file type
        setUploadStatus('failed');
        setFile(droppedFile);
      }
    }
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (config.allowedFileTypes.some(type => selectedFile.name.toLowerCase().endsWith(type))) {
        setUploadStatus('uploading');
        setUploadProgress(0);
        
        // Simulate upload progress
        const interval = setInterval(() => {
          setUploadProgress(prev => {
            if (prev >= 100) {
              clearInterval(interval);
              setUploadStatus('uploaded');
              return 100;
            }
            return prev + 10;
          });
        }, 100);
        
        setFile(selectedFile);
        // Clear resume field error when file is selected
        if (fieldErrors.resume) {
          setFieldErrors(prev => ({ ...prev, resume: undefined }));
        }
      } else {
        // Unsupported file type
        setUploadStatus('failed');
        setFile(selectedFile);
      }
    }
  };

  // Analyze resume
  const analyzeResume = async () => {
    // Clear previous field errors
    setFieldErrors({});
    
    // Validate fields
    const errors: { resume?: string; jobDescription?: string } = {};
    
    if (!file) {
      errors.resume = 'Please upload a resume file.';
    }
    
    if (!jobDescription.trim()) {
      errors.jobDescription = 'Please paste a job description.';
    } else if (jobDescription.trim().length < 50) {
      errors.jobDescription = 'Please paste a longer job description with role-specific details.';
    }
    
    // If there are validation errors, show them and focus the first invalid field
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      
      // Focus and scroll to the first invalid field
      if (errors.resume) {
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        if (fileInput) {
          fileInput.focus();
          fileInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      } else if (errors.jobDescription) {
        const textarea = document.querySelector('textarea') as HTMLTextAreaElement;
        if (textarea) {
          textarea.focus();
          textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
      
      return;
    }

    // Trigger animation replay on each click
    setAnimationRunId(prev => prev + 1);

    // Reset state to avoid stale data
    setResults(null);
    setIsAnalyzing(true);

    
    const formData = new FormData();
    formData.append('resume_file', file!); // We know file is not null due to validation above
    formData.append('job_description', jobDescription);

    try {
      console.log('Sending request to:', `${config.backendUrl}${config.endpoints.analyze}`);
      console.log('File:', file!.name, 'Size:', file!.size);
      console.log('Job description length:', jobDescription.length);
      
      const response = await fetch(`${config.backendUrl}${config.endpoints.analyze}`, {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const text = await response.text().catch(() => '');
        console.error('Response text:', text);
        throw new Error(`HTTP ${response.status}: ${text || 'Request failed'}`);
      }
      
      const data = await response.json().catch((e) => {
        console.error('JSON parse error:', e);
        return null;
      });
      
      console.log('Response data:', data);
      
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid response from server');
      }
      
      // Enhanced debugging for missing keywords issue
      console.log('=== ENHANCED DEBUG: Missing Keywords Issue ===');
      console.log('Raw API response:', JSON.stringify(data, null, 2));
      console.log('- all_keywords:', data.all_keywords);
      console.log('- matched_keywords:', data.matched_keywords);
      console.log('- missing_keywords:', data.missing_keywords);
      console.log('- bullet_suggestions:', data.bullet_suggestions);
      console.log('- Field access test:');
      console.log('  * data.missing_keywords:', data.missing_keywords);
      console.log('  * data.missing_keywords?.length:', data.missing_keywords?.length);
      console.log('  * Array.isArray(data.missing_keywords):', Array.isArray(data.missing_keywords));
      console.log('  * typeof data.missing_keywords:', typeof data.missing_keywords);
      console.log('  * data.missing_keywords === null:', data.missing_keywords === null);
      console.log('  * data.missing_keywords === undefined:', data.missing_keywords === undefined);
      console.log('  * data.missing_keywords === []:', JSON.stringify(data.missing_keywords) === '[]');
      console.log('  * JSON.stringify(data.missing_keywords):', JSON.stringify(data.missing_keywords));
      console.log('=====================================');
      
      // Check if the response contains an error status
      if (data.status === 'error') {
        console.log('Backend returned error:', data.message);
        setResults({ error: data.message });
        return;
      }
      
      console.log('Setting results with data:', data);
      setResults(data as any);

    } catch (error) {
      console.error('Analysis failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setResults({ error: errorMessage });

    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">


      {/* Main Content - Responsive Layout */}
      <div className="flex flex-col lg:flex-row flex-1 min-h-0">
        {/* Left Panel - Input Section */}
        <div 
          className={`bg-[#F2F2F2] flex flex-col transition-all duration-300 ${
            results ? 'lg:w-1/2 lg:flex-shrink-0' : 'w-full lg:w-1/2 lg:flex-shrink-0'
          }`}
          style={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: 'calc(100vh - clamp(2rem, 2.5vw, 2.5rem))', // 100vh minus footer height
            height: 'calc(100vh - clamp(2rem, 2.5vw, 2.5rem))',
            overflow: 'hidden'
          }}
        >
          {/* Content Block - Header, description, file upload, job description */}
          <div 
            style={{
              display: 'flex',
              padding: 'clamp(1.5rem, 4vh, 2.5rem) clamp(2rem, 5vw, 5.625rem)',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              flex: '1 1 auto',
              overflow: 'hidden',
              minHeight: 0,
              gap: '0' // Remove gap, use explicit spacing
            }}
          >
            {/* Text Block - Header + Description */}
            <div 
              className="w-full"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '0.25rem',
                alignSelf: 'stretch',
                maxWidth: '100%',
                overflow: 'hidden',
                boxSizing: 'border-box',
                width: '100%'
              }}
            >
              {/* Main Heading - Flexible size #000000 */}
              <h2 className="font-ibm-condensed font-extralight text-black leading-tight"
                style={{ 
                  fontSize: 'clamp(2rem, 6vw, 3rem)',
                  width: 'fit-content',
                  maxWidth: '100%',
                  wordWrap: 'break-word',
                  overflowWrap: 'break-word'
                }}>
              Is your resume ATS-ready?
            </h2>
            
              {/* Description - Flexible size #575656 */}
              <p className="font-ibm-condensed font-extralight text-[#575656] leading-relaxed"
                style={{ 
                  fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                  width: 'fit-content',
                  maxWidth: '100%',
                  wordWrap: 'break-word',
                  overflowWrap: 'break-word'
                }}>
              Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.
            </p>
            </div>
            
            {/* Spacing between Header/Description and Upload Section */}
            <div style={{ height: 'clamp(2.5rem, 3vw, 3rem)' }}></div>

            {/* Upload File Component */}
            <div 
              className="w-full"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '0.75rem',
                alignSelf: 'stretch'
              }}
            >
              {/* Title "Your Resume" Flexible size #000000 */}
              <h3 className="font-ibm-condensed font-extralight text-black"
                style={{ fontSize: 'clamp(0.875rem, 2vw, 1rem)' }}>
                Your Resume
              </h3>
              
              {/* Drag and drop field + description */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                  alignSelf: 'stretch'
                }}
              >
                {/* Upload Field - Fixed Height Container */}
                <motion.div
                  className="transition-opacity duration-200 upload-container"
                  aria-invalid={fieldErrors.resume ? 'true' : 'false'}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center', // Center content vertically
                    padding: 'clamp(0.4rem, 1.2vw, 0.6rem) clamp(0.75rem, 2vw, 1rem)',
                    alignSelf: 'stretch',
                    borderRadius: '4px',
                    background: '#FFFFFF',
                    minHeight: fieldErrors.resume ? 'clamp(4rem, 9vh, 4.5rem)' : 'clamp(3.5rem, 8vh, 4rem)', // Flexible height when error is present
                    width: '100%',
                    boxSizing: 'border-box',
                    border: fieldErrors.resume ? '1px solid #E7640E' : '1px solid #E5E7EB'
                  }}
                  onDrop={handleDrop}
                  onDragOver={(e) => {
                    e.preventDefault();
                    e.currentTarget.style.border = '1px dashed #000';
                    e.currentTarget.style.background = '#F0F2EF';
                  }}
                  onDragEnter={(e) => {
                    e.preventDefault();
                    e.currentTarget.style.border = '1px dashed #000';
                    e.currentTarget.style.background = '#F0F2EF';
                  }}
                  onDragLeave={(e) => {
                    e.preventDefault();
                    e.currentTarget.style.border = fieldErrors.resume ? '1px solid #E7640E' : '1px solid #E5E7EB';
                    e.currentTarget.style.background = '#FFFFFF';
                  }}
                  onDragExit={(e) => {
                    e.preventDefault();
                    e.currentTarget.style.border = fieldErrors.resume ? '1px solid #E7640E' : '1px solid #E5E7EB';
                    e.currentTarget.style.background = '#FFFFFF';
                  }}
                  animate={{
                    borderColor: fieldErrors.resume ? '#E7640E' : (uploadStatus === 'failed' ? '#E7640E' : 'transparent'),
                    background: '#FFFFFF'
                  }}
                  transition={{ duration: 0.2 }}
                >
                  {uploadStatus === 'uploading' ? (
                    /* Uploading resume state */
                    <div className="flex items-center justify-between w-full">
                      <div className="flex items-center gap-4">
                        {/* Show failedfile icon if file type is not supported, otherwise show file type icon */}
                        {(!file?.name.toLowerCase().endsWith('.pdf') && !file?.name.toLowerCase().endsWith('.doc') && !file?.name.toLowerCase().endsWith('.docx')) ? (
                          <img src="/icons/failedfile.svg" alt="Failed File" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        ) : (
                          <>
                            {file?.name.toLowerCase().endsWith('.pdf') && (
                              <img src="/icons/pdf.svg" alt="PDF" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                            )}
                            {file?.name.toLowerCase().endsWith('.doc') && (
                              <img src="/icons/doc.svg" alt="DOC" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                            )}
                            {file?.name.toLowerCase().endsWith('.docx') && (
                              <img src="/icons/docx.svg" alt="DOCX" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                            )}
                          </>
                        )}
                        <div className="flex flex-col">
                          <span className="text-[16px] font-ibm-condensed font-extralight text-black">
                            {file?.name} is uploading
                          </span>
                          <span className="text-[12px] font-ibm-condensed font-extralight text-gray-500">
                            Uploaded {uploadProgress}%
                          </span>
                        </div>
                      </div>
                      
                      {/* Round loader instead of button */}
                      <div className="w-6 h-6 flex-shrink-0">
                        <svg 
                          xmlns="http://www.w3.org/2000/svg" 
                          width="24" 
                          height="24" 
                          viewBox="0 0 24 24" 
                          fill="none"
                          style={{ transform: 'rotate(-90deg)' }}
                        >
                          <mask id="path-1-inside-1_607_23015" fill="white">
                            <path d="M12 0C18.6274 0 24 5.37258 24 12C24 18.6274 18.6274 24 12 24C5.37258 24 0 18.6274 0 12C0 5.37258 5.37258 0 12 0Z"/>
                          </mask>
                          <g clipPath="url(#paint0_angular_607_23015_clip_path)" data-figma-skip-parse="true" mask="url(#path-1-inside-1_607_23015)">
                            <g transform="matrix(-0.012 0 0 -0.012 12 12)">
                              <foreignObject x="-1291.67" y="-1291.67" width="2583.33" height="2583.33">
                                <div style={{
                                  background: `conic-gradient(from 90deg, rgba(255, 255, 255, 0) 0deg, rgba(156, 207, 116, 1) ${uploadProgress * 3.6}deg, rgba(255, 255, 255, 0) 360deg)`,
                                  height: '100%',
                                  width: '100%',
                                  opacity: 1
                                }}></div>
                              </foreignObject>
                            </g>
                          </g>
                          <path d="M12 0V3.5C16.6944 3.5 20.5 7.30558 20.5 12H24H27.5C27.5 3.43959 20.5604 -3.5 12 -3.5V0ZM24 12H20.5C20.5 16.6944 16.6944 20.5 12 20.5V24V27.5C20.5604 27.5 27.5 20.5604 27.5 12H24ZM12 24V20.5C7.30558 20.5 3.5 16.6944 3.5 12H0H-3.5C-3.5 20.5604 3.43959 27.5 12 27.5V24ZM0 12H3.5C3.5 7.30558 7.30558 3.5 12 3.5V0V-3.5C3.43959 -3.5 -3.5 3.43959 -3.5 12H0Z" data-figma-gradient-fill="{&quot;type&quot;:&quot;GRADIENT_ANGULAR&quot;,&quot;stops&quot;:[{&quot;color&quot;:{&quot;r&quot;:1.0,&quot;g&quot;:1.0,&quot;b&quot;:1.0,&quot;a&quot;:0.0},&quot;position&quot;:0.0},{&quot;color&quot;:{&quot;r&quot;:0.61176472902297974,&quot;g&quot;:0.81176471710205078,&quot;b&quot;:0.45490196347236633,&quot;a&quot;:1.0},&quot;position&quot;:1.0}],&quot;stopsVar&quot;:[{&quot;color&quot;:{&quot;r&quot;:1.0,&quot;g&quot;:1.0,&quot;b&quot;:1.0,&quot;a&quot;:0.0},&quot;position&quot;:0.0},{&quot;color&quot;:{&quot;r&quot;:0.61176472902297974,&quot;g&quot;:0.81176471710205078,&quot;b&quot;:0.45490196347236633,&quot;a&quot;:1.0},&quot;position&quot;:1.0}],&quot;transform&quot;:{&quot;m00&quot;:-24.0,&quot;m01&quot;:-2.9309887850104133e-14,&quot;m02&quot;:24.0,&quot;m10&quot;:2.6645352591003757e-14,&quot;m11&quot;:-24.0,&quot;m12&quot;:24.0},&quot;opacity&quot;:1.0,&quot;blendMode&quot;:&quot;NORMAL&quot;,&quot;visible&quot;:true}" mask="url(#path-1-inside-1_607_23015)"/>
                          <defs>
                            <clipPath id="paint0_angular_607_23015_clip_path">
                              <path d="M12 0V3.5C16.6944 3.5 20.5 7.30558 20.5 12H24H27.5C27.5 3.43959 20.5604 -3.5 12 -3.5V0ZM24 12H20.5C20.5 16.6944 16.6944 20.5 12 20.5V24V27.5C20.5604 27.5 27.5 20.5604 27.5 12H24ZM12 24V20.5C7.30558 20.5 3.5 16.6944 3.5 12H0H-3.5C-3.5 20.5604 3.43959 27.5 12 27.5V24ZM0 12H3.5C3.5 7.30558 7.30558 3.5 12 3.5V0V-3.5C3.43959 -3.5 -3.5 3.43959 -3.5 12H0Z" mask="url(#path-1-inside-1_607_23015)"/>
                            </clipPath>
                          </defs>
                        </svg>
                      </div>
                    </div>
                  ) : uploadStatus === 'uploaded' && file ? (
                    /* File uploaded state - Same size as default field */
                    <div className="flex items-center justify-between w-full">
                      <div className="flex items-center gap-4">
                        {/* Icon of file which is uploaded (pdf/docx/doc) – custom icon from my folder */}
                        {file.name.toLowerCase().endsWith('.pdf') && (
                          <img src="/icons/pdf.svg" alt="PDF" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        )}
                        {file.name.toLowerCase().endsWith('.doc') && (
                          <img src="/icons/doc.svg" alt="DOC" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        )}
                        {file.name.toLowerCase().endsWith('.docx') && (
                          <img src="/icons/docx.svg" alt="DOCX" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        )}
                        <span className="text-[16px] font-ibm-condensed font-extralight text-black">
                      {file.name}
                        </span>
                      </div>
                      
                      {/* Button with icon instead of browse button */}
                      <button
                        onClick={() => {
                          setFile(null);
                          setUploadStatus('idle');
                          setUploadProgress(0);
                        }}
                        className="w-6 h-6 flex justify-center items-center flex-shrink-0 hover:bg-[#d9d9d9] active:outline-none active:ring-0 active:ring-0 active:border-0 transition-colors"
                        style={{ color: '#000000' }}
                      >
                        <img src="/icons/close.svg" alt="Remove" style={{ width: 'clamp(1rem, 3vw, 1.25rem)', height: 'clamp(1rem, 3vw, 1.25rem)' }} />
                      </button>
                    </div>
                  ) : uploadStatus === 'failed' ? (
                    /* Failed state */
                    <div className="flex items-center justify-between w-full">
                      <div className="flex items-center gap-4">
                        {/* Failed file icon - always show failedfile icon */}
                        <img src="/icons/failedfile.svg" alt="Failed File" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        <div className="flex flex-col">
                          <span className="text-[16px] font-ibm-condensed font-extralight" style={{ color: '#737373' }}>
                            {file?.name}
                          </span>
                          <span className="text-[12px] font-ibm-condensed font-extralight" style={{ color: '#E7640E' }}>
                            Failed to Upload
                          </span>
                        </div>
                      </div>
                      
                      {/* Action buttons */}
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            setUploadStatus('uploading');
                            setUploadProgress(0);
                            
                            // Simulate upload attempt that will fail again
                            setTimeout(() => {
                              setUploadStatus('failed');
                            }, 2000);
                          }}
                          className="w-6 h-6 flex justify-center items-center flex-shrink-0 hover:bg-[#d9d9d9] active:outline-none active:ring-0 active:border-0 transition-colors"
                          style={{ color: '#E7640E' }}
                        >
                          <img src="/icons/retry.svg" alt="Retry" style={{ width: '20px', height: '20px' }} />
                        </button>
                    <button
                          onClick={() => {
                            setFile(null);
                            setUploadStatus('idle');
                            setUploadProgress(0);
                          }}
                          className="w-6 h-6 flex justify-center items-center flex-shrink-0 hover:bg-[#d9d9d9] active:outline-none active:ring-0 active:border-0 transition-colors"
                          style={{ color: '#000000' }}
                        >
                          <img src="/icons/close.svg" alt="Remove" style={{ width: '20px', height: '20px' }} />
                    </button>
                      </div>
                  </div>
                ) : (
                    /* Default state */
                    <div className="flex items-center justify-between w-full">
                      {/* Icon + "drag and drop" text - Hidden on mobile/tablet */}
                      <div 
                        className="hidden lg:flex flex-col gap-1"
                        style={{ width: '340px' }}
                      >
                        <div className="flex items-center gap-4">
                          <img src="/icons/resume.svg" alt="Resume" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                          <div className="flex flex-col">
                            <span className="text-[16px] font-ibm-condensed font-extralight text-black">
                              drag and drop file here
                            </span>
                            {fieldErrors.resume && (
                              <span className="text-[12px] font-ibm-condensed font-extralight" style={{ color: '#E7640E' }}>
                                {fieldErrors.resume}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {/* Mobile/Tablet: Show icon + text */}
                      <div className="lg:hidden flex flex-col gap-1">
                        <div className="flex items-center gap-4">
                          <img src="/icons/resume.svg" alt="Resume" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                          <div className="flex flex-col">
                            <span className="font-ibm-condensed font-extralight text-black"
                              style={{ fontSize: 'clamp(0.75rem, 2vw, 0.875rem)' }}>
                              Tap Upload to add resume
                            </span>
                            {fieldErrors.resume && (
                              <span className="font-ibm-condensed font-extralight" 
                                style={{ 
                                  fontSize: 'clamp(0.625rem, 1.5vw, 0.75rem)',
                                  color: '#E7640E' 
                                }}>
                                {fieldErrors.resume}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                      aria-invalid={fieldErrors.resume ? 'true' : 'false'}
                      aria-describedby={fieldErrors.resume ? 'resume-error' : undefined}
                    />
                      
                      {/* Browse/Upload button - styled like primary button */}
                    <label
                      htmlFor="file-upload"
                        className="cursor-pointer inline-flex h-9 px-6 justify-center items-center gap-2 flex-shrink-0 rounded-sm font-ibm-condensed font-extralight text-[16px] transition-all duration-200 active:outline-none active:ring-0 active:border-0"
                        style={{
                          borderRadius: '2px',
                          background: '#000000',
                          color: '#FFFFFF',
                          padding: 'clamp(0.25rem, 1vw, 0.25rem) clamp(1rem, 3vw, 1.5rem)',
                          height: 'clamp(2rem, 5vh, 2.25rem)',
                          fontSize: 'clamp(0.75rem, 2vw, 0.875rem)'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = '#2f2f2f';
                          e.currentTarget.style.color = '#FFFFFF';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = '#000000';
                          e.currentTarget.style.color = '#FFFFFF';
                        }}
                        onMouseDown={(e) => {
                          e.currentTarget.style.background = '#000000';
                          e.currentTarget.style.color = '#FFFFFF';
                        }}
                        onMouseUp={(e) => {
                          e.currentTarget.style.background = '#000000';
                          e.currentTarget.style.color = '#FFFFFF';
                        }}
                    >
                      <span className="hidden lg:inline">Browse</span>
                      <span className="lg:hidden">Upload</span>
                    </label>
                  </div>
                )}
                </motion.div>
                
                {/* Description: Fixed height container to prevent layout jumps */}
                <div 
                  className="font-ibm-condensed font-extralight"
                  style={{ 
                    height: 'clamp(1rem, 2.5vh, 1.25rem)', // Fixed height
                    fontSize: 'clamp(0.625rem, 1.5vw, 0.75rem)',
                    lineHeight: 'clamp(1rem, 2.5vh, 1.25rem)', // Match height
                    display: 'flex',
                    alignItems: 'center'
                  }}>
                  {uploadStatus === 'idle' && (
                    <span style={{ color: '#737373' }}>
                      Limit 200MB per file. Supported file types: PDF, DOC, DOCX
                    </span>
                  )}
                  {uploadStatus === 'failed' && !fieldErrors.resume && (
                    <span style={{ color: '#E7640E' }}>
                      {file?.name.toLowerCase().endsWith('.png') || file?.name.toLowerCase().endsWith('.jpg') || file?.name.toLowerCase().endsWith('.jpeg') || file?.name.toLowerCase().endsWith('.gif') ? 'Image files (.png, .jpg, .jpeg, .gif) are not supported. Please upload a PDF, DOC, or DOCX file.' : file?.name.toLowerCase().endsWith('.txt') ? 'Text files (.txt) are not supported. Please upload a PDF, DOC, or DOCX file.' : file && file.size > 200 * 1024 * 1024 ? 'File size exceeds 200MB limit. Please choose a smaller file.' : 'Upload failed due to an error. Please check your file and try again.'}
                    </span>
                  )}
                  {uploadStatus === 'uploading' && !fieldErrors.resume && (
                    <span style={{ color: '#737373' }}>
                      Uploading your resume... Please wait.
                    </span>
                  )}
                  {uploadStatus === 'uploaded' && !fieldErrors.resume && (
                    <span style={{ color: 'transparent', visibility: 'hidden' }}>
                      &nbsp; {/* Invisible placeholder to maintain height */}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Spacing between Upload and Job Description */}
            <div style={{ height: '32px' }}></div>

            {/* Job Description Component */}
            <div 
              className="w-full"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '0.75rem',
                flex: '1 1 auto',
                alignSelf: 'stretch',
                minHeight: '200px',
                overflow: 'visible' // Allow focus outline to be visible
              }}
            >
              {/* Title "Job Description" Flexible size #000000 */}
              <h3 className="font-ibm-condensed font-extralight text-black"
                style={{ fontSize: 'clamp(0.875rem, 2vw, 1rem)' }}>
                Job Description
              </h3>
              
              {/* Textarea + Error Message Container */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  gap: '0.5rem',
                  alignSelf: 'stretch',
                  flex: '1 1 auto' // Fill available space
                }}
              >
                {/* Text Field - Fill Available Space */}
                <textarea
                  placeholder="Paste the job description here..." 
                  value={jobDescription}
                  onChange={(e) => {
                    setJobDescription(e.target.value);
                    // Clear job description field error when user types
                    if (fieldErrors.jobDescription && e.target.value.trim()) {
                      setFieldErrors(prev => ({ ...prev, jobDescription: undefined }));
                    }
                  }}
                  onDoubleClick={(e) => (e.target as HTMLTextAreaElement).select()}
                  className="w-full resize-none font-ibm-condensed font-extralight job-description-textarea"
                  aria-invalid={fieldErrors.jobDescription ? 'true' : 'false'}
                  aria-describedby={fieldErrors.jobDescription ? 'job-description-error' : undefined}
                  style={{
                    flex: '1 1 auto', // Fill available space
                    minHeight: 'clamp(8rem, 15vh, 10rem)', // Minimum height
                    borderRadius: '6px',
                    background: '#FFFFFF',
                    color: jobDescription ? '#000000' : '#737373',
                    cursor: 'text',
                    resize: 'none',
                    fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                    lineHeight: '1.5',
                    outline: 'none',
                    transition: 'none',
                    padding: 'clamp(0.75rem, 1.5vw, 1rem)',
                    boxSizing: 'border-box'
                  }}
                  onFocus={() => setIsTyping(true)}
                  onBlur={() => setIsTyping(false)}
                />
              
                {/* Error Message Container - Fixed height to prevent layout jumps */}
                <div 
                  className="font-ibm-condensed font-extralight"
                  style={{ 
                    height: 'clamp(1rem, 2.5vh, 1.25rem)', // Fixed height to match upload component
                    fontSize: 'clamp(0.625rem, 1.5vw, 0.75rem)',
                    lineHeight: 'clamp(1rem, 2.5vh, 1.25rem)', // Match height
                    display: 'flex',
                    alignItems: 'center'
                  }}>
                  {fieldErrors.jobDescription && (
                    <span 
                      id="job-description-error"
                      style={{ color: '#E7640E' }}
                    >
                      {fieldErrors.jobDescription}
                    </span>
                  )}
                </div>
              </div>
              
            </div>

            {/* Spacing between Job Description and Privacy Policy */}
            <div style={{ height: '32px' }}></div>

            {/* Privacy Consent Text */}
            <div 
              className="w-full"
              style={{
                paddingBottom: '4px' // Extra space for focus ring
              }}
            >
              <p 
                className="font-ibm-condensed text-left"
                style={{
                  fontSize: 'clamp(0.75rem, 1.5vw, 0.875rem)', // 12-14px range
                  color: '#737373', // Neutral gray color
                  lineHeight: '1.4',
                  margin: 0
                }}
              >
                By clicking "Get My Score", you agree to the{' '}
                <a 
                  href="/privacy" 
                  className="privacy-link"
                  style={{
                    color: '#0088FF',
                    textDecoration: 'none',
                    padding: '4px 6px',
                    margin: '0 2px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.textDecoration = 'underline';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.textDecoration = 'none';
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.outline = '2px solid #000000';
                    e.currentTarget.style.outlineOffset = '2px';
                    e.currentTarget.style.borderRadius = '0px';
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.outline = 'none';
                  }}
                >
                  Privacy Policy
                </a>
                .
              </p>
            </div>

            {/* Spacing between Privacy Policy and Buttons */}
            <div style={{ height: '40px' }}></div>

          </div>

          {/* Buttons Block - Sticks to all borders, NO spacing */}
          <div 
            className="w-full flex-shrink-0 bg-[#F2F2F2]"
            style={{
              display: 'flex',
              alignItems: 'stretch',
              alignSelf: 'stretch',
              padding: '0',
              margin: '0',
              borderTop: 'none'
            }}
          >
            <div className="flex flex-col sm:flex-row gap-0 w-full"
              style={{
                padding: '0'
              }}>
              {/* Start Over Button - Secondary Button - NO STROKE ON ACTIVE */}
              <button
                onClick={() => {
                  // Cleanup all animations first
                  cleanupAnimations();
                  
                  // Reset all state
                  setFile(null);
                  setJobDescription('');
                  setResults(null);
                  setAnimatedScore(0);
                  setPreviousScore(0);
                  setAnimatedTextSimilarity(0);
                  setPreviousTextSimilarity(0);
                  setAnimatedKeywordCoverage(0);
                  setPreviousKeywordCoverage(0);
                              setAnimatedKeywordCount(0);
            setPreviousKeywordCount(0);
            setAnimatedAtsBarWidth(0);
            setAnimatedKeywordCoverageBarWidth(0);
                  
                  // Reset animation tracking refs
                  lastResultsRef.current = null;
                  isNewResultsRef.current = false;
                  setAnimationRunId(0);
                }}
                className="hidden sm:block flex-1 font-ibm-condensed font-extralight border-0 text-black bg-[#ebebeb] hover:bg-[#f8f8f8] focus:bg-[#ebebeb] focus:outline-none active:bg-[#ebebeb] active:outline-none active:ring-0 active:border-0 transition-all flex items-center justify-center"
                style={{
                  height: 'clamp(3.5rem, 10vh, 5rem)',
                  padding: 'clamp(0.75rem, 2vw, 1.5rem)',
                  fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                  borderRight: '1px solid #d1d5db'
                }}
              >
                Start Over
              </button>
              
              {/* Get My Score Button - Primary Button - IBM Extra Light 200 */}
              <button
                onClick={analyzeResume}
                className="flex-1 font-ibm-condensed font-extralight border-0 bg-black text-white hover:bg-[#2f2f2f] active:bg-black active:outline-none active:ring-0 active:border-0 transition-all flex items-center justify-center"
                style={{
                  height: 'clamp(3.5rem, 10vh, 5rem)',
                  padding: 'clamp(0.75rem, 2vw, 1.5rem)',
                  fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                }}
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

        {/* Visual Divider */}
        <div className="hidden lg:block w-px bg-gray-200 flex-shrink-0"></div>
        
        {/* Right Panel - Always show on large screens */}
        <div 
          className="transition-all duration-300 hidden lg:block lg:w-1/2 lg:flex-shrink-0 bg-white"
          style={{
            height: 'calc(100vh - clamp(2rem, 2.5vw, 2.5rem))',
            overflow: results && !results.error ? 'auto' : 'hidden'
          }}
        >
          <div className="w-full relative z-10">
          

          {results && (results as any).error && (
            /* Error State - Friendly unreadable file card */
            <div 
              className="w-full h-full flex items-center justify-center overflow-auto"
              style={{
                height: '100%',
                padding: 'clamp(1.5rem, 4vh, 2.5rem) clamp(2rem, 5vw, 5.625rem)'
              }}
            >
              <div 
                className="w-full flex justify-center items-center"
                role="alert" 
                aria-live="polite"
              >
                <div 
                  className="bg-slate-50 border border-slate-200 rounded-2xl shadow-sm p-4 sm:p-6 space-y-3 sm:space-y-4 dark:bg-slate-900 dark:border-slate-700 text-center"
                  style={{ maxWidth: '720px', width: '100%' }}
                >
                  {/* Icon */}
                  <div className="flex items-center justify-center gap-3">
                    <div 
                      className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-lg"
                      aria-hidden="true"
                    >
                      🤖
                    </div>
                  </div>

                  {/* Title and lead text */}
                  <div className="space-y-2">
                    <p 
                      className="font-ibm-condensed text-gray-800 dark:text-gray-200 text-sm sm:text-sm leading-relaxed"
                      style={{ whiteSpace: 'pre-line', lineHeight: '1.45' }}
                    >
                      <span className="font-semibold">Most likely this document isn't machine-readable — the bots are seeing vibes, not text.</span>
                      {'\n'}Quick fix: export from Google Docs/Word as PDF (text stays selectable).
                      {'\n'}Using Canva? Download as PDF (Print/Standard), no "Flatten PDF", and keep text editable.
                    </p>
                  </div>

                  {/* Bullet list */}
                  <div>
                    <p className="font-ibm-condensed font-semibold text-gray-800 dark:text-gray-200 text-sm mb-3">
                      Most common reasons:
                    </p>
                    <ul 
                      className="font-ibm-condensed text-gray-700 dark:text-gray-300 text-sm leading-relaxed space-y-1"
                      style={{ paddingLeft: '18px' }}
                    >
                      <li className="flex items-start gap-2">
                        <span className="text-green-600 dark:text-green-400 mt-0.5">✓</span>
                        <span>It's a scan/photo — the text is just an image.</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-600 dark:text-green-400 mt-0.5">✓</span>
                        <span>Text was outlined or the PDF was flattened (non-selectable).</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-600 dark:text-green-400 mt-0.5">✓</span>
                        <span>The file is encrypted/password-protected or digitally signed.</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-600 dark:text-green-400 mt-0.5">✓</span>
                        <span>The export came out malformed (over-"optimized" or "print to PDF" quirks).</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-600 dark:text-green-400 mt-0.5">✓</span>
                        <span>Weird letter spacing from a design export (hello, Figma — S P A C E D letters).</span>
                      </li>
                    </ul>
                  </div>

                  {/* Self-check line */}
                  <p 
                    className="font-ibm-condensed text-gray-600 dark:text-gray-400 text-sm italic opacity-80 mt-3"
                    style={{ marginTop: '12px' }}
                  >
                    Quick self-check: if you can Select + Copy the text in the PDF, bots can too.
                  </p>
                </div>
              </div>
            </div>
          )}
          
          {results && !results.error ? (
              /* Results Display */
              <div 
                style={{
                  padding: 'clamp(1.5rem, 4vh, 2.5rem) clamp(2rem, 5vw, 5.625rem) clamp(2rem, 4vh, 3rem) clamp(2rem, 5vw, 5.625rem)'
                }}
              >

                {/* Hero ATS Score Section */}
                <div>
                  <h2 className="font-ibm-condensed font-extralight text-[#737373] mb-2" style={{
                    fontSize: screenWidth <= 768 ? '14px' : screenWidth <= 1024 ? '16px' : '18px'
                  }}>
                    Your ATS match score
                  </h2>
                  <div 
                    className="font-ibm-condensed font-extralight text-[#000000] mb-6" 
                    style={{
                      fontSize: screenWidth <= 768 ? '28px' : screenWidth <= 1024 ? '32px' : '36px',
                      fontVariantNumeric: 'tabular-nums' // Prevent width shifts during animation
                    }}
                    aria-live="polite"
                    aria-label={`ATS match score: ${results && !results.error ? animatedScore : 0} out of 100`}
                  >
                    <span style={{ fontVariantNumeric: 'tabular-nums' }}>
                      {results && !results.error ? animatedScore : 0}
                    </span>/100
                  </div>
                  
                  {/* Single Progress Bar for Overall ATS Score */}
                  <div className="w-full" style={{ height: '32px', marginBottom: '16px' }}>
                    <div className="relative w-full h-full bg-gray-200 overflow-hidden">
                                            {/* Gradient fill up to score percentage */}
                      <div 
                        className="h-full"
                        style={{
                          width: '100%',
                          background: 'linear-gradient(to right, #F79D00 0%, #FFD700 30%, #64F38C 100%)',
                          clipPath: `inset(0 ${100 - (results && !results.error ? animatedAtsBarWidth : 0)}% 0 0)`
                        }}
                      />
                      
                      {/* Mask effect - 3px ticks covering entire bar width */}
                      <div className="absolute top-0 left-0 w-full h-full">
                        {Array.from({ length: Math.ceil((screenWidth || 1920) / 6) }, (_, index) => (
                          <div
                            key={index}
                            className="absolute top-0 h-full"
                            style={{
                              left: `${index * 6}px`,
                              width: '3px',
                              backgroundColor: '#ffffff'
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Sub-scores Section */}
                <div className="flex justify-between">
                  <div>
                    <h3 className="font-ibm-condensed font-extralight text-[#737373] mb-1" style={{
                      fontSize: screenWidth <= 768 ? '10px' : screenWidth <= 1024 ? '11px' : '12px'
                    }}>
                      Text similarity
                    </h3>
                    <div 
                      className="font-ibm-condensed font-extralight text-[#000000]" 
                      style={{
                        fontSize: screenWidth <= 768 ? '20px' : screenWidth <= 1024 ? '24px' : '30px',
                        fontVariantNumeric: 'tabular-nums',
                        minWidth: '3ch', // Reserve space for 3 characters (e.g., "100")
                        textAlign: 'left'
                      }}
                      aria-live="polite"
                      aria-label={`Text similarity: ${(() => {
                        const value = results && !results.error ? animatedTextSimilarity : 0;
                        const finalValue = results && !results.error ? results.textSimilarity : 0;
                        return finalValue === 0 ? 0 : Math.max(1, Math.round(value));
                      })()} percent`}
                    >
                      <span style={{ fontVariantNumeric: 'tabular-nums' }}>
                        {(() => {
                          const value = results && !results.error ? animatedTextSimilarity : 0;
                          const finalValue = results && !results.error ? results.textSimilarity : 0;
                          // Show 0 only if final value is 0, otherwise show at least 1 during animation
                          return finalValue === 0 ? 0 : Math.max(1, Math.round(value));
                        })()}
                      </span>%
                    </div>
                  </div>
                  <div>
                    <h3 className="font-ibm-condensed font-extralight text-[#737373] mb-1" style={{
                      fontSize: screenWidth <= 768 ? '10px' : screenWidth <= 1024 ? '11px' : '12px'
                    }}>
                      Keyword coverage
                    </h3>
                    <div 
                      className="font-ibm-condensed font-extralight text-[#000000]" 
                      style={{
                        fontSize: screenWidth <= 768 ? '20px' : screenWidth <= 1024 ? '24px' : '30px',
                        fontVariantNumeric: 'tabular-nums',
                        minWidth: '3ch', // Reserve space for 3 characters (e.g., "100")
                        textAlign: 'left'
                      }}
                      aria-live="polite"
                      aria-label={`Keyword coverage: ${(() => {
                        const value = results && !results.error ? animatedKeywordCoverage : 0;
                        const finalValue = results && !results.error ? results.keywordCoverage : 0;
                        return finalValue === 0 ? 0 : Math.max(1, Math.round(value));
                      })()} percent`}
                    >
                      <span style={{ fontVariantNumeric: 'tabular-nums' }}>
                        {(() => {
                          const value = results && !results.error ? animatedKeywordCoverage : 0;
                          const finalValue = results && !results.error ? results.keywordCoverage : 0;
                          // Show 0 only if final value is 0, otherwise show at least 1 during animation
                          return finalValue === 0 ? 0 : Math.max(1, Math.round(value));
                        })()}
                      </span>%
                    </div>
                  </div>
                </div>

                {/* Detailed Content Block - Responsive Layout */}
                <div className="w-full" style={{ 
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  gap: '24px',
                  marginTop: '40px'
                }}>
                  {/* Keyword Coverage Block */}
                  <div style={{ width: '100%' }}>
                    <h3 className="font-ibm-condensed font-extralight text-[#000000] mb-4" style={{
                      fontSize: screenWidth <= 768 ? '14px' : screenWidth <= 1024 ? '16px' : '18px'
                    }}>
                      Keyword Coverage
                    </h3>
                    
                    <KeywordCoverage 
                      current={results && !results.error ? Math.round(animatedKeywordCount) : 0} 
                      total={results?.all_keywords?.length || 0} 
                      screenWidth={screenWidth}
                      animatedBarWidth={results && !results.error ? animatedKeywordCoverageBarWidth : undefined}
                    />
                  </div>

                  {/* Keywords Section */}
                  <div style={{ width: '100%' }}>
                    <h3 className="font-ibm-condensed font-extralight text-[#000000] mb-4" style={{
                      fontSize: screenWidth <= 768 ? '14px' : screenWidth <= 1024 ? '16px' : '18px'
                    }}>
                      All JD Keywords (Top 30)
                    </h3>
                    
                    {/* Keywords Grid */}
                    <div className="flex flex-wrap mb-6" style={{ 
                      width: '100%', 
                      minWidth: '0',
                      marginTop: 'clamp(12px, 3vw, 18px)'
                    }}>
                      {(results?.all_keywords || []).map((keyword: string, index: number) => (
                        <div key={index} style={{ marginBottom: '4px', marginRight: '4px' }}>
                          <span
                            style={{
                              display: 'flex',
                              padding: screenWidth <= 768 ? '3px 6px' : screenWidth <= 1024 ? '4px 8px' : '5px 10px',
                              justifyContent: 'center',
                              alignItems: 'center',
                              borderRadius: screenWidth <= 768 ? '1px' : '2px',
                              backgroundColor: 'rgba(225, 228, 223, 0.5)',
                              color: '#000000',
                              fontFamily: 'IBM Plex Sans Condensed',
                              fontWeight: '200',
                              fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px',
                              minHeight: screenWidth <= 768 ? '20px' : screenWidth <= 1024 ? '22px' : '24px'
                            }}
                          >
                            {keyword}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Present in Resume + Missing Keywords - Responsive Grid Layout */}
                    <div className="grid grid-cols-1 gap-6 sm:gap-8 lg:gap-10 items-start" style={{ 
                      marginTop: '24px',
                      gridTemplateColumns: screenWidth <= 1363 ? '1fr' : 'repeat(2, 1fr)'
                    }}>
                      {/* Present in Resume */}
                      <div className="grid grid-rows-[auto_auto_auto] gap-2 sm:gap-3">
                        {/* Icon + Title */}
                        <div className="flex items-center gap-1 mb-2 sm:mb-3">
                          <img
                            src="/icons/Check.svg"
                            alt="present"
                            style={{
                              width: '20px',
                              height: '20px'
                            }}
                          />
                          <span className="font-ibm-condensed font-extralight text-[#000000] ml-1">
                            Present in your resume
                          </span>
                        </div>
                        
                        {/* Pill Container - Responsive spacing and height */}
                        <div className="flex flex-wrap items-start content-start justify-start leading-none" style={{ 
                          gap: '4px',
                          minHeight: screenWidth <= 1363 ? 'auto' : (screenWidth <= 1600 ? '50px' : '60px'),
                          marginBottom: '18px'
                        }}>
                          {(results?.matched_keywords ?? []).map((keyword: string, index: number) => (
                            <span
                              key={index}
                              className="leading-none"
                              style={{
                                display: 'flex',
                                padding: screenWidth <= 768 ? '3px 6px' : screenWidth <= 1024 ? '4px 8px' : '5px 10px',
                                justifyContent: 'center',
                                alignItems: 'center',
                                borderRadius: screenWidth <= 768 ? '1px' : '2px',
                                backgroundColor: 'rgba(177, 236, 130, 0.5)',
                                color: '#000000',
                                fontFamily: 'IBM Plex Sans Condensed',
                                fontWeight: '200',
                                fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px',
                                height: screenWidth <= 768 ? '20px' : screenWidth <= 1024 ? '22px' : '24px',
                                lineHeight: '1'
                              }}
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                        
                        {/* Description Text */}
                                <p 
          className="font-ibm-condensed font-extralight text-[#737373]" 
          style={{
            fontSize: screenWidth <= 768 ? '10px' : screenWidth <= 1024 ? '11px' : '12px',
            fontVariantNumeric: 'tabular-nums'
          }}
          aria-live="polite"
          aria-label={`Great job! You're covering ${results && !results.error ? results.matched_keywords?.length || 0 : 0} out of ${results?.all_keywords?.length || 0} top JD keywords`}
        >
          Great job! You're covering <span style={{ fontVariantNumeric: 'tabular-nums' }}>{results && !results.error ? results.matched_keywords?.length || 0 : 0}</span> out of <span style={{ fontVariantNumeric: 'tabular-nums' }}>{results?.all_keywords?.length || 0}</span> top JD keywords
        </p>
                      </div>

                      {/* Missing Keywords */}
                      <div className="grid grid-rows-[auto_auto_auto] gap-2 sm:gap-3">
                        {/* Icon + Title */}
                        <div className="flex items-center gap-1 mb-2 sm:mb-3">
                          <img
                            src="/icons/Cancel.svg"
                            alt="missing"
                            style={{
                              width: '20px',
                              height: '20px'
                            }}
                          />
                          <span className="font-ibm-condensed font-extralight text-[#000000] ml-1">
                            Missing / low-visibility keywords
                          </span>
                        </div>
                        
                        {/* Pill Container - Responsive spacing and height */}
                        <div className="flex flex-wrap items-start content-start justify-start leading-none" style={{ 
                          gap: '4px',
                          minHeight: screenWidth <= 1363 ? 'auto' : (screenWidth <= 1600 ? '50px' : '60px'),
                          marginBottom: '18px'
                        }}>
                          {(results?.missing_keywords ?? []).map((keyword: string, index: number) => (
                            <span
                              key={index}
                              className="leading-none"
                              style={{
                                display: 'flex',
                                padding: screenWidth <= 768 ? '3px 6px' : screenWidth <= 1024 ? '4px 8px' : '5px 10px',
                                justifyContent: 'center',
                                alignItems: 'center',
                                borderRadius: screenWidth <= 768 ? '1px' : '2px',
                                backgroundColor: 'rgba(230, 35, 1, 0.5)',
                                color: '#000000',
                                fontFamily: 'IBM Plex Sans Condensed',
                                fontWeight: '200',
                                fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px',
                                height: screenWidth <= 768 ? '20px' : screenWidth <= 1024 ? '22px' : '24px',
                                lineHeight: '1'
                              }}
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                        
                        {/* Description Text */}
                        <p className="font-ibm-condensed font-extralight text-[#737373]" style={{
                          fontSize: screenWidth <= 768 ? '10px' : screenWidth <= 1024 ? '11px' : '12px'
                        }}>
                          Showing top 7 most relevant missing keywords. Add these to improve your coverage.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Divider */}
                  <div style={{
                    width: '100%',
                    height: '1px',
                    backgroundColor: '#F0F1EF',
                    margin: '0 0 24px 0'
                  }} />

                  {/* Bullet Suggestions */}
                  <div className="pb-6" style={{ width: '100%' }}>
                    <h3 className="font-ibm-condensed font-extralight text-[#000000] mb-4" style={{
                      fontSize: screenWidth <= 768 ? '14px' : screenWidth <= 1024 ? '16px' : '18px'
                    }}>
                      Bullet Suggestions (add these to your resume):
                    </h3>
                    
                    {results?.bullet_suggestions && results.bullet_suggestions.length > 0 ? (
                      <ul className="space-y-3 mb-4">
                                                {results.bullet_suggestions.map((bullet: string, index: number) => (
                          <li 
                            key={index}
                            className="flex items-start gap-3 font-ibm-condensed font-extralight text-[#000000]"
                            style={{
                              fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px'
                            }}
                          >
                            <span className="w-2 h-2 bg-black rounded-full mt-2 flex-shrink-0" />
                            <span 
                              dangerouslySetInnerHTML={{ 
                                __html: highlightKeywords(bullet, results?.missing_keywords || []) 
                              }}
                            />
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500 italic mb-4">
                        No bullet suggestions available. Upload a resume and job description to get personalized suggestions.
                      </p>
                    )}

                    {/* Tip */}
                    <div className="flex items-center gap-3 p-4 rounded-lg" style={{
                      backgroundColor: '#F3F3F3'
                    }}>
                      <span style={{
                        fontSize: screenWidth <= 768 ? 16 : screenWidth <= 1024 ? 18 : 20
                      }}>💡</span>
                      <span className="font-ibm-condensed font-extralight text-[#000000]" style={{
                        fontSize: screenWidth <= 768 ? 12 : screenWidth <= 1024 ? 13 : 14
                      }}>
                        Tip: Customize these bullets with your specific metrics and achievements.
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : !results || (!(results as any).error && Object.keys(fieldErrors).length === 0) ? (
              /* Empty State - Simple placeholder (only when no results and no error) */
              <div 
                className="w-full h-full flex items-center justify-center"
                style={{
                  height: '100%',
                  minHeight: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: 'clamp(1.5rem, 4vh, 2.5rem) clamp(2rem, 5vw, 5.625rem)'
                }}
              >
                <div className="text-center" style={{ maxWidth: '400px' }}>
                  <h3 className="text-xl font-ibm-condensed font-extralight text-gray-500 mb-4" style={{
                    fontSize: 'clamp(1.125rem, 2.5vw, 1.25rem)',
                    lineHeight: '1.4'
                  }}>
                    Upload your resume to get started
                  </h3>
                  <p className="font-ibm-condensed font-extralight text-gray-400" style={{
                    fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                    lineHeight: '1.5'
                  }}>
                    Your ATS compatibility results will appear here
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
      {/* Footer */}
      <footer 
        className="w-full border-t border-gray-200 flex-shrink-0"
        style={{
          height: 'clamp(2rem, 2.5vw, 2.5rem)', // 40px on 1920px, scales down
          minHeight: '2rem',
          backgroundColor: '#F2F2F2'
        }}
      >
        <div className="flex items-center justify-between h-full px-6">
          {/* Left side - Copyright */}
          <div 
            className="font-ibm-condensed font-extralight text-black"
            style={{
              fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
            }}
          >
            © 2025 | All rights reserved
          </div>
          
          {/* Right side - Links */}
          <div className="flex items-center gap-6">
            <a 
              href="/faq" 
              className="font-ibm-condensed font-extralight text-black hover:underline transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              style={{
                fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
              }}
            >
              FAQ
            </a>
            <a 
              href="/privacy" 
              className="font-ibm-condensed font-extralight text-black hover:underline transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              style={{
                fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
              }}
            >
              Privacy Policy
            </a>
            <a 
              href="/terms" 
              className="font-ibm-condensed font-extralight text-black hover:underline transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              style={{
                fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
              }}
            >
              Terms & Conditions
            </a>
          </div>
        </div>
      </footer>


    </div>
  );
}
