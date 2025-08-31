'use client';

import { useState, useEffect } from 'react';
import { Upload, Search, FileText, CheckCircle, AlertCircle, RefreshCw, BarChart3 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { config } from '../config';
import KeywordCoverage from '../components/KeywordCoverage';

// Force Vercel to detect changes and deploy latest updates
// Latest commit: Custom icons added, syntax errors fixed, ready for deployment
// Vercel deployment trigger - significant change to force rebuild
export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>({
    // Mock data for development - remove this in production
    score: 55,
    textSimilarity: 65,
    keywordCoverage: 70,
    keywords: ['interaction', 'figma', 'user', 'accessibility', 'prototyping', 'testing', 'product', 'data', 'gathering', 'improvements'],
    missingKeywords: ['directly', 'generation', 'hypothesis', 'insight', 'ideation', 'implementation', 'execution']
  });
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'failed'>('checking');
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'uploaded' | 'failed'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [screenWidth, setScreenWidth] = useState(0);

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

  // Test backend connection
  const testConnection = async () => {
    console.log('Vercel deployment test - connection function called');
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
      } else {
        // Unsupported file type
        setUploadStatus('failed');
        setFile(selectedFile);
      }
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
        <div 
          className={`bg-[#F2F2F2] flex flex-col transition-all duration-300 ${
            results ? 'lg:w-1/2 lg:flex-shrink-0' : 'w-full'
          }`}
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            overflow: 'hidden',
            minHeight: '100vh'
          }}
        >
          {/* Content Block - Header, description, file upload, job description */}
          <div 
            style={{
              display: 'flex',
              padding: 'clamp(3rem, 8vh, 5rem) clamp(2rem, 5vw, 5.625rem) 0 clamp(2rem, 5vw, 5.625rem)',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: 'clamp(2rem, 4vh, 3.5rem)',
              flex: '1 1 auto',
              overflow: 'hidden',
              marginBottom: 'clamp(2rem, 4vh, 3rem)'
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
                alignSelf: 'stretch'
              }}
            >
              {/* Main Heading - Flexible size #000000 */}
              <h2 className="font-ibm-condensed font-extralight text-black leading-tight"
                style={{ fontSize: 'clamp(2rem, 6vw, 3rem)' }}>
              Is your resume ATS-ready?
            </h2>
            
              {/* Description - Flexible size #575656 */}
              <p className="font-ibm-condensed font-extralight text-[#575656] leading-relaxed"
                style={{ fontSize: 'clamp(0.875rem, 2vw, 1rem)' }}>
              Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.
            </p>
            </div>
            


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
                {/* Upload Field - Drag and drop fields (desktop only) */}
                <motion.div
                  className={`transition-all duration-200`}
                  style={{
                    display: 'flex',
                    padding: 'clamp(0.5rem, 1.5vw, 0.75rem) clamp(0.75rem, 2vw, 1rem)',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    alignSelf: 'stretch',
                    borderRadius: '4px',
                    background: '#FFFFFF',
                    border: 'none',
                    minHeight: 'clamp(3rem, 8vh, 3.75rem)',
                    height: 'auto',
                    width: '100%'
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
                    e.currentTarget.style.border = 'none';
                    e.currentTarget.style.background = '#FFFFFF';
                  }}
                  onDragExit={(e) => {
                    e.preventDefault();
                    e.currentTarget.style.border = 'none';
                    e.currentTarget.style.background = '#FFFFFF';
                  }}
                  animate={{
                    border: uploadStatus === 'failed' ? '1px solid #E7640E' : 
                           uploadStatus === 'uploaded' ? 'none' : 'none',
                    background: uploadStatus === 'uploaded' ? '#FFFFFF' : '#FFFFFF'
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
                              <img src="/icons/Property 1=PDF.svg" alt="PDF" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                            )}
                            {file?.name.toLowerCase().endsWith('.doc') && (
                              <img src="/icons/Property 1=DOC.svg" alt="DOC" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                            )}
                            {file?.name.toLowerCase().endsWith('.docx') && (
                              <img src="/icons/Property 1=DOCX.svg" alt="DOCX" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
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
                          <img src="/icons/Property 1=PDF.svg" alt="PDF" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        )}
                        {file.name.toLowerCase().endsWith('.doc') && (
                          <img src="/icons/Property 1=DOC.svg" alt="DOC" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        )}
                        {file.name.toLowerCase().endsWith('.docx') && (
                          <img src="/icons/Property 1=DOCX.svg" alt="DOCX" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
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
                        <img src="/icons/Property 1=close.svg" alt="Remove" style={{ width: 'clamp(1rem, 3vw, 1.25rem)', height: 'clamp(1rem, 3vw, 1.25rem)' }} />
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
                          <img src="/icons/Property 1=Component 31, Property 2=Variant6.svg" alt="Retry" style={{ width: '20px', height: '20px' }} />
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
                          <img src="/icons/Property 1=close.svg" alt="Remove" style={{ width: '20px', height: '20px' }} />
                    </button>
                      </div>
                  </div>
                ) : (
                    /* Default state */
                    <div className="flex items-center justify-between w-full">
                      {/* Icon + "drag and drop" text - Hidden on mobile/tablet */}
                      <div 
                        className="hidden lg:flex items-center gap-4"
                        style={{ width: '340px' }}
                      >
                        <img src="/icons/resume.svg" alt="Resume" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        <span className="text-[16px] font-ibm-condensed font-extralight text-black">
                          drag and drop file here
                        </span>
                      </div>
                      
                      {/* Mobile/Tablet: Show icon + text */}
                      <div className="lg:hidden flex items-center gap-4">
                        <img src="/icons/resume.svg" alt="Resume" style={{ width: 'clamp(2rem, 5vw, 2.5rem)', height: 'clamp(2rem, 5vw, 2.5rem)' }} />
                        <span className="font-ibm-condensed font-extralight text-black"
                          style={{ fontSize: 'clamp(0.75rem, 2vw, 0.875rem)' }}>
                          Tap Upload to add resume
                        </span>
                      </div>
                      
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
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
                
                {/* Description: Always show to maintain consistent height */}
                <p className="font-ibm-condensed font-extralight min-h-[1rem]"
                  style={{ fontSize: 'clamp(0.625rem, 1.5vw, 0.75rem)' }}>
                  {uploadStatus === 'idle' && (
                    <span style={{ color: '#737373' }}>
                      Limit 200MB per file. Supported file types: PDF, DOC, DOCX
                    </span>
                  )}
                  {uploadStatus === 'failed' && (
                    <span style={{ color: '#E7640E' }}>
                      {file?.name.toLowerCase().endsWith('.png') || file?.name.toLowerCase().endsWith('.jpg') || file?.name.toLowerCase().endsWith('.jpeg') || file?.name.toLowerCase().endsWith('.gif') ? 'Image files (.png, .jpg, .jpeg, .gif) are not supported. Please upload a PDF, DOC, or DOCX file.' : file?.name.toLowerCase().endsWith('.txt') ? 'Text files (.txt) are not supported. Please upload a PDF, DOC, or DOCX file.' : file && file.size > 200 * 1024 * 1024 ? 'File size exceeds 200MB limit. Please choose a smaller file.' : 'Upload failed due to an error. Please check your file and try again.'}
                    </span>
                  )}
                  {uploadStatus === 'uploading' && (
                    <span style={{ color: '#737373' }}>
                      Uploading your resume... Please wait.
                    </span>
                  )}
                  {uploadStatus === 'uploaded' && (
                    <span style={{ color: 'transparent' }}>
                      &nbsp;
                    </span>
                  )}
                </p>
              </div>
            </div>



            {/* Job Description Component */}
            <div 
              className="w-full"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '0.75rem',
                flex: '1 1 auto',
                alignSelf: 'stretch'
              }}
            >
              {/* Title "Job Description" Flexible size #000000 */}
              <h3 className="font-ibm-condensed font-extralight text-black"
                style={{ fontSize: 'clamp(0.875rem, 2vw, 1rem)' }}>
                Job Description
              </h3>
              
              {/* Text Field */}
              <textarea
                placeholder="Paste the job description here..." 
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                onFocus={() => setIsTyping(true)}
                onBlur={() => setIsTyping(false)}
                onDoubleClick={(e) => (e.target as HTMLTextAreaElement).select()}
                className="w-full resize-none font-ibm-condensed font-extralight transition-all duration-200 focus:outline-none focus:ring-0" 
                style={{
                  minHeight: 'clamp(6rem, 15vh, 8rem)',
                  height: 'auto',
                  flex: '1 1 auto',
                  padding: 'clamp(0.75rem, 2vw, 1rem)',
                  borderRadius: '6px',
                  background: '#FFFFFF',
                  border: isTyping ? '1px solid #000000' : 'none',
                  color: jobDescription ? '#000000' : '#737373',
                  outline: 'none',
                  cursor: 'text',
                  resize: 'none',
                  fontSize: 'clamp(0.875rem, 2vw, 1rem)'
                }}
                onMouseEnter={(e) => {
                  if (!isTyping) {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.border = '1px solid #E9E9E9';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isTyping) {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.border = 'none';
                  }
                }}
              />
              

              
              {/* Description: Show error only on error state */}
              {jobDescription && jobDescription.length < 50 && (
                <p className="font-ibm-condensed font-extralight" 
                  style={{ 
                    color: '#E7640E',
                    fontSize: 'clamp(0.625rem, 1.5vw, 0.75rem)'
                  }}>
                  Job description must be at least 50 characters long. Current: {jobDescription.length} characters.
                </p>
              )}
            </div>
            

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
                  setFile(null);
                  setJobDescription('');
                  setResults(null);
                }}
                className="hidden sm:block flex-1 font-ibm-condensed font-extralight border-0 text-black bg-[#ebebeb] hover:bg-[#f8f8f8] focus:bg-[#ebebeb] focus:outline-none focus:ring-0 focus:ring-offset-0 active:bg-[#ebebeb] active:outline-none active:ring-0 active:border-0 transition-all flex items-center justify-center"
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

        {/* Right Panel - Results Section - Equal sizing with left panel */}
        <div className={`bg-white transition-all duration-300 ${
          results ? 'block lg:w-1/2 lg:flex-shrink-0' : 'hidden lg:block lg:w-1/2 lg:flex-shrink-0'
        }`}
        style={{
          overflow: results ? 'auto' : 'hidden'
        }}>
          <div className="w-full">
            {!results && (
              /* Empty State */
              <div 
                className="text-center"
                style={{
                  padding: 'clamp(3rem, 8vh, 5rem) clamp(2rem, 5vw, 5.625rem) clamp(2rem, 4vh, 3rem) clamp(2rem, 5vw, 5.625rem)'
                }}
              >
                <BarChart3 className="h-24 w-24 text-gray-300 mx-auto mb-6" />
                <h3 className="text-2xl font-ibm-condensed font-extralight text-gray-400 mb-4">
                  Ready to analyze your resume?
                </h3>
                <p className="font-ibm-condensed font-extralight text-gray-500">
                  Upload your resume and paste a job description to get started.
                </p>
              </div>
            )}
            
            {results && results.error && (
              /* Error State */
              <div 
                className="text-center"
                style={{
                  padding: 'clamp(3rem, 8vh, 5rem) clamp(2rem, 5vw, 5.625rem) clamp(2rem, 4vh, 3rem) clamp(2rem, 5vw, 5.625rem)'
                }}
              >
                <AlertCircle className="h-24 w-24 text-red-300 mx-auto mb-6" />
                <h3 className="text-2xl font-ibm-condensed font-extralight text-red-600 mb-4">
                  Analysis Failed
                </h3>
                <p className="font-ibm-condensed font-extralight text-red-500">
                  {results.error}
                </p>
              </div>
            )}
            
            {results && !results.error && (
              /* Results Display */
              <div 
                style={{
                  padding: 'clamp(3rem, 8vh, 5rem) clamp(2rem, 5vw, 5.625rem) clamp(2rem, 4vh, 3rem) clamp(2rem, 5vw, 5.625rem)'
                }}
              >
                {/* Hero ATS Score Section */}
                <div>
                  <h2 className="font-ibm-condensed font-extralight text-[#737373] mb-2" style={{
                    fontSize: screenWidth <= 768 ? '14px' : screenWidth <= 1024 ? '16px' : '18px'
                  }}>
                    Your ATS match score
                  </h2>
                  <div className="font-ibm-condensed font-extralight text-[#000000] mb-6" style={{
                    fontSize: screenWidth <= 768 ? '28px' : screenWidth <= 1024 ? '32px' : '36px'
                  }}>
                    {results.score}/100
                  </div>
                  
                  {/* Single Progress Bar for Overall ATS Score */}
                  <div className="w-full" style={{ height: '32px', marginBottom: '16px' }}>
                    <div className="relative w-full h-full bg-gray-200 overflow-hidden">
                                            {/* Gradient fill up to score percentage */}
                      <div 
                        className="h-full transition-all duration-1000"
                        style={{
                          width: '100%',
                          background: 'linear-gradient(to right, #F79D00 0%, #FFD700 30%, #64F38C 100%)',
                          clipPath: `inset(0 ${100 - results.score}% 0 0)`
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
                    <h3 className="font-ibm-condensed font-extralight text-[#737373] text-sm mb-1">
                      Text similarity
                    </h3>
                    <div className="font-ibm-condensed font-extralight text-[#000000]" style={{
                      fontSize: screenWidth <= 768 ? '20px' : screenWidth <= 1024 ? '24px' : '30px'
                    }}>
                      {results.textSimilarity}%
                    </div>
                  </div>
                  <div>
                    <h3 className="font-ibm-condensed font-extralight text-[#737373] mb-1" style={{
                      fontSize: screenWidth <= 768 ? '10px' : screenWidth <= 1024 ? '11px' : '12px'
                    }}>
                      Keyword coverage
                    </h3>
                    <div className="font-ibm-condensed font-extralight text-[#000000]" style={{
                      fontSize: screenWidth <= 768 ? '20px' : screenWidth <= 1024 ? '24px' : '30px'
                    }}>
                      {results.keywordCoverage}%
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
                    
                    <KeywordCoverage current={11} total={30} screenWidth={screenWidth} />
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
                      {['product', 'insight', 'prototyping', 'user', 'testing', 'accessibility', 'figma', 'streaming', 'interaction', 'directly', 'implementation', 'gathering', 'perspectives', 'supplier', 'visual', 'shape', 'data', 'generation', 'execution', 'multinational', 'intersection', 'discover', 'screens', 'lifecycle', 'hypothesis', 'ideation', 'translate', 'actionable', 'improvements'].map((keyword, index) => (
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
                            src="/icons/check.svg"
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
                          {results.keywords.map((keyword: string, index: number) => (
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
                        <p className="font-ibm-condensed font-extralight text-[#737373]" style={{
                          fontSize: screenWidth <= 768 ? '10px' : screenWidth <= 1024 ? '11px' : '12px'
                        }}>
                          Great job! You're covering 11 out of 30 top JD keywords
                        </p>
                      </div>

                      {/* Missing Keywords */}
                      <div className="grid grid-rows-[auto_auto_auto] gap-2 sm:gap-3">
                        {/* Icon + Title */}
                        <div className="flex items-center gap-1 mb-2 sm:mb-3">
                          <img
                            src="/icons/cancel.svg"
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
                          {results.missingKeywords.map((keyword: string, index: number) => (
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
                    
                    <ul className="space-y-3 mb-4">
                      {[
                        'Conducted user research that provided **insights** driving 3 major product decisions',
                        'Generated **insights** from analytics data that improved conversion by 35%',
                        'Designed streaming platform interfaces used by 100K+ users',
                        'Established visual design standards that improved brand consistency across 5+ products'
                      ].map((bullet, index) => (
                        <li 
                          key={index}
                          className="flex items-start gap-3 font-ibm-condensed font-extralight text-[#000000]"
                          style={{
                            fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px'
                          }}
                        >
                          <span className="w-2 h-2 bg-black rounded-full mt-2 flex-shrink-0" />
                          <span dangerouslySetInnerHTML={{
                            __html: bullet.replace(/\*\*(.*?)\*\*/g, '<span style="font-weight: 500;">$1</span>')
                          }} />
                        </li>
                      ))}
                    </ul>

                    {/* Tip */}
                    <div className="flex items-center gap-3 p-4 rounded-lg" style={{
                      backgroundColor: '#F3F3F3'
                    }}>
                      <span style={{
                        fontSize: screenWidth <= 768 ? '16px' : screenWidth <= 1024 ? '18px' : '20px'
                      }}>💡</span>
                      <span className="font-ibm-condensed font-extralight text-[#000000]" style={{
                        fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px'
                      }}>
                        Tip: Customize these bullets with your specific metrics and achievements.
                      </span>
                    </div>
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
