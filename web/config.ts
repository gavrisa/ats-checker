// Configuration file for the ATS Resume Checker
export const config = {
  // Backend API URL - change this if your backend is deployed elsewhere
  backendUrl: process.env.NEXT_PUBLIC_API_URL || 'https://ats-checker-r82q.onrender.com',
  
  // API endpoints
  endpoints: {
    health: '/health',
    analyze: '/analyze',
  },
  
  // File upload settings
  maxFileSize: 10 * 1024 * 1024, // 10MB
  allowedFileTypes: ['.pdf', '.docx', '.txt'],
};
