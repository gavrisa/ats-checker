// Configuration file for the ATS Resume Checker
export const config = {
  // Backend API URL - change this if your backend is deployed elsewhere
  backendUrl: process.env.NEXT_PUBLIC_API_URL || 
    (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
      ? 'http://localhost:8000' 
      : 'https://ats-checker-cz1i.onrender.com'),
  
  // API endpoints
  endpoints: {
    health: '/health',
    analyze: '/analyze',
  },
  
  // File upload settings
  maxFileSize: 200 * 1024 * 1024, // 200MB
  allowedFileTypes: ['.pdf', '.doc', '.docx'],
};
