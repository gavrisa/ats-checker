'use client';

import { useState } from 'react';
import { Upload, Search, FileText, CheckCircle, AlertCircle, RefreshCw, BarChart3 } from 'lucide-react';
import { config } from '../config';

// Force Vercel to detect changes and deploy latest updates
// Latest commit: Font cleanup, IBM Plex only, perfect button specs
export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'failed'>('checking');
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'uploaded' | 'failed'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);

  // Test backend connection
  const testConnection = async () => {
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
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && config.allowedFileTypes.some(type => droppedFile.name.toLowerCase().endsWith(type))) {
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
    }
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
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
        <div className="w-full lg:w-1/2 bg-[#F2F2F2] overflow-hidden flex flex-col">
          {/* Content Area - Exact CSS specifications */}
          <div 
            className="flex-1 px-[90px]"
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: '56px',
              flex: '1 0 0',
              alignSelf: 'stretch',
              paddingTop: '80px',
              width: '100%'
            }}
          >
            {/* Text Block - Header + Description */}
            <div 
              className="w-full"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '4px',
                alignSelf: 'stretch'
              }}
            >
              {/* Main Heading - 48px #000000 */}
              <h2 className="text-[48px] font-ibm-condensed font-extralight text-black leading-tight">
                Is your resume ATS-ready?
              </h2>
              
              {/* Description - 16px #575656 */}
              <p className="text-[16px] font-ibm-condensed font-extralight text-[#575656] leading-relaxed">
                Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.
              </p>
            </div>
            


            {/* Upload File Component */}
            <div 
              className="w-[580px]"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '12px'
              }}
            >
              {/* Title "Your Resume" 16px #000000 */}
              <h3 className="text-[16px] font-ibm-condensed font-extralight text-black">
                Your Resume
              </h3>
              
              {/* Drag and drop field + description */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  gap: '8px',
                  alignSelf: 'stretch'
                }}
              >
                {/* Upload Field - Drag and drop fields */}
                <div
                  className={`transition-all duration-200`}
                  style={{
                    display: 'flex',
                    padding: '12px 16px',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    alignSelf: 'stretch',
                    borderRadius: '4px',
                    background: '#FFFFFF',
                    border: '1px solid #000000',
                    minHeight: '60px'
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
                    e.currentTarget.style.border = '1px solid #000000';
                    e.currentTarget.style.background = '#FFFFFF';
                  }}
                  onDragExit={(e) => {
                    e.preventDefault();
                    e.currentTarget.style.border = '1px solid #000000';
                    e.currentTarget.style.background = '#FFFFFF';
                  }}
                >
                  {uploadStatus === 'uploading' ? (
                    /* Uploading resume state */
                    <div className="flex items-center justify-between w-full">
                      <div className="flex items-center gap-4">
                        {/* Icon of file which is uploaded (pdf/docx/doc) – custom icon from my folder */}
                        {file?.name.toLowerCase().endsWith('.pdf') && (
                          <img src="/icons/PDF.svg" alt="PDF" className="h-6 w-6" />
                        )}
                        {file?.name.toLowerCase().endsWith('.doc') && (
                          <img src="/icons/DOC.svg" alt="DOC" className="h-6 w-6" />
                        )}
                        {file?.name.toLowerCase().endsWith('.docx') && (
                          <img src="/icons/DOCX.svg" alt="DOCX" className="h-6 w-6" />
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
                    /* File uploaded state */
                    <div className="flex items-center justify-between w-full">
                      <div className="flex items-center gap-4">
                        {/* Icon of file which is uploaded (pdf/docx/doc) – custom icon from my folder */}
                        {file.name.toLowerCase().endsWith('.pdf') && (
                          <img src="/icons/PDF.svg" alt="PDF" className="h-6 w-6" />
                        )}
                        {file.name.toLowerCase().endsWith('.doc') && (
                          <img src="/icons/DOC.svg" alt="DOC" className="h-6 w-6" />
                        )}
                        {file.name.toLowerCase().endsWith('.docx') && (
                          <img src="/icons/DOCX.svg" alt="DOCX" className="h-6 w-6" />
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
                        className="w-6 h-6 flex justify-center items-center flex-shrink-0 hover:bg-[#d9d9d9] active:outline-none active:ring-0 active:border-0 transition-colors"
                        style={{ color: '#323232' }}
                      >
                        <img src="/icons/Cancel.svg" alt="Remove" className="h-4 w-4" />
                      </button>
                    </div>
                  ) : uploadStatus === 'failed' ? (
                    /* Failed state */
                    <div className="flex items-center justify-between w-full">
                      <div className="flex items-center gap-4">
                        {/* Icon of file which is uploaded (pdf/docx/doc) – custom icon from my folder */}
                        {file?.name.toLowerCase().endsWith('.pdf') && (
                          <img src="/icons/PDF.svg" alt="PDF" className="h-6 w-6 opacity-50" />
                        )}
                        {file?.name.toLowerCase().endsWith('.doc') && (
                          <img src="/icons/DOC.svg" alt="DOC" className="h-6 w-6 opacity-50" />
                        )}
                        {file?.name.toLowerCase().endsWith('.docx') && (
                          <img src="/icons/DOCX.svg" alt="DOCX" className="h-6 w-6 opacity-50" />
                        )}
                        <div className="flex flex-col">
                          <span className="text-[16px] font-ibm-condensed font-extralight text-black">
                            {file?.name}
                          </span>
                          <span className="text-[12px] font-ibm-condensed font-extralight text-orange-500">
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
                          }}
                          className="w-6 h-6 flex justify-center items-center flex-shrink-0 hover:bg-[#d9d9d9] active:outline-none active:ring-0 active:border-0 transition-colors"
                          style={{ color: '#323232' }}
                        >
                          <img src="/icons/Property 1=Component 31, Property 2=Variant6.svg" alt="Retry" className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            setFile(null);
                            setUploadStatus('idle');
                            setUploadProgress(0);
                          }}
                          className="w-6 h-6 flex justify-center items-center flex-shrink-0 hover:bg-[#d9d9d9] active:outline-none active:ring-0 active:border-0 transition-colors"
                          style={{ color: '#323232' }}
                        >
                          <img src="/icons/Cancel.svg" alt="Remove" className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* Default state */
                    <div className="flex items-center justify-between w-full">
                      {/* Icon + "drag and drop" text */}
                      <div 
                        className="flex items-center gap-4"
                        style={{ width: '340px' }}
                      >
                        <img src="/icons/resume.svg" alt="Resume" className="h-6 w-6" />
                        <span className="text-[16px] font-ibm-condensed font-extralight text-black">
                          drag and drop file here
                        </span>
                      </div>
                      
                      <input
                        type="file"
                        accept=".pdf,.doc,.docx"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="file-upload"
                      />
                      
                      {/* Browse button */}
                      <label
                        htmlFor="file-upload"
                        className="cursor-pointer inline-flex h-9 px-6 justify-center items-center gap-2 flex-shrink-0 rounded-sm font-ibm-condensed font-extralight text-[16px] transition-all duration-200 active:outline-none active:ring-0 active:border-0"
                        style={{
                          borderRadius: '2px',
                          background: '#000000',
                          color: '#000000',
                          padding: '4px 24px'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = '#2F2F2F';
                          e.currentTarget.style.color = '#000000';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = '#000000';
                          e.currentTarget.style.color = '#000000';
                        }}
                        onMouseDown={(e) => {
                          e.currentTarget.style.border = '1px solid #000';
                          e.currentTarget.style.color = '#000000';
                        }}
                        onMouseUp={(e) => {
                          e.currentTarget.style.border = 'none';
                          e.currentTarget.style.color = '#000000';
                        }}
                      >
                        Browse
                      </label>
                    </div>
                  )}
                </div>
                
                {/* Description: "Limit 200MB per file. Supported file types: PDF, DOC, DOCX" 12px #737373 */}
                <p className="text-[12px] font-ibm-condensed font-extralight text-[#737373]">
                  Limit 200MB per file. Supported file types: PDF, DOC, DOCX
                </p>
              </div>
            </div>
            


            {/* Text Field Component */}
            <div 
              className="w-full"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '12px',
                flex: '1 0 0',
                alignSelf: 'stretch'
              }}
            >
              {/* Title "Job Description" 16px #000000 */}
              <label className="block font-ibm-condensed font-extralight text-[16px] text-black">
                Job Description
              </label>
              
              {/* Text field - width fill content block, height fill content block but so content block and buttons should be spacing 48px */}
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                className="w-full border border-black rounded-md resize-none font-ibm-condensed font-extralight text-[12px] text-[#737373] focus:outline-none focus:ring-0 focus:border-black transition-colors"
                style={{ 
                  height: '200px', // Fixed height to ensure proper spacing
                  padding: '16px'
                }}
              />
            </div>
            

          </div>

          {/* Action Buttons - Stick to right, left, and bottom with no spacing */}
          <div 
            className="flex-shrink-0"
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              alignSelf: 'stretch'
            }}
          >
            <div className="flex flex-col sm:flex-row gap-0 w-full">
              {/* Start Over Button - Secondary Button - NO STROKE ON ACTIVE */}
              <button
                onClick={() => {
                  setFile(null);
                  setJobDescription('');
                  setResults(null);
                }}
                className="hidden sm:block flex-1 h-16 sm:h-[72px] lg:h-[80px] px-6 font-ibm-condensed font-extralight text-base border-0 text-black bg-[#ebebeb] hover:bg-[#f8f8f8] focus:bg-[#ebebeb] focus:outline-none focus:ring-0 focus:ring-offset-0 active:bg-[#ebebeb] active:outline-none active:ring-0 active:border-0 transition-all flex items-center justify-center"
              >
                Start Over
              </button>
              
              {/* Get My Score Button - Primary Button - IBM Extra Light 200 */}
              <button
                onClick={analyzeResume}
                className="flex-1 h-16 sm:h-[72px] lg:h-[80px] px-6 font-ibm-condensed font-extralight text-base border-0 bg-black text-white hover:bg-[#2f2f2f] active:bg-black active:outline-none active:ring-0 active:border-0 transition-all flex items-center justify-center"
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

        {/* Right Panel - Results Section */}
        <div className="w-full lg:w-1/2 bg-white p-6 sm:p-8 lg:p-8 xl:p-8 2xl:p-8 overflow-y-auto">
          <div className="max-w-2xl mx-auto">
            {!results ? (
              /* Empty State */
              <div className="text-center py-20">
                <BarChart3 className="h-24 w-24 text-gray-300 mx-auto mb-6" />
                <h3 className="text-2xl font-ibm-condensed font-extralight text-gray-400 mb-4">
                  Ready to analyze your resume?
                </h3>
                <p className="font-ibm-condensed font-extralight text-gray-500">
                  Upload your resume and paste a job description to get started.
                </p>
              </div>
            ) : results.error ? (
              /* Error State */
              <div className="text-center py-20">
                <AlertCircle className="h-24 w-24 text-red-300 mx-auto mb-6" />
                <h3 className="text-2xl font-ibm-condensed font-extralight text-red-600 mb-4">
                  Analysis Failed
                </h3>
                <p className="font-ibm-condensed font-extralight text-red-500">
                  {results.error}
                </p>
              </div>
            ) : (
              /* Results Display */
              <div className="space-y-6">
                <h3 className="text-2xl font-ibm-condensed font-extralight text-gray-800 mb-6">
                  Analysis Results
                </h3>
                
                {/* ATS Score */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800">
                      ATS Match Score
                    </h4>
                    <span className="text-3xl font-ibm-condensed font-extralight text-blue-600">
                      {results.ats_score}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${results.ats_score}%` }}
                    />
                  </div>
                </div>

                {/* Keywords Found */}
                <div className="bg-green-50 p-6 rounded-xl border border-green-200">
                  <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800 mb-4">
                    Keywords Found
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {results.keywords_found?.map((keyword: string, index: number) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-ibm-condensed font-extralight text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Missing Keywords */}
                <div className="bg-red-50 p-6 rounded-xl border border-red-200">
                  <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800 mb-4">
                    Missing Keywords
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {results.keywords_missing?.map((keyword: string, index: number) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-ibm-condensed font-extralight text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>

                {/* File Info */}
                <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
                  <h4 className="text-lg font-ibm-condensed font-extralight text-gray-800 mb-4">
                    File Information
                  </h4>
                  <div className="space-y-2 font-ibm-condensed font-extralight text-sm text-gray-600">
                    <p><strong>Filename:</strong> {results.file_info?.filename}</p>
                    <p><strong>Size:</strong> {(results.file_info?.size / 1024).toFixed(1)} KB</p>
                    <p><strong>Type:</strong> {results.file_info?.content_type}</p>
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
