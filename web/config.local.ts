// Local development configuration for the ATS Resume Checker
export const config = {
  // Backend API URL - local development
  backendUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // API endpoints
  endpoints: {
    health: '/health',
    analyze: '/analyze',
  },
  
  // File upload settings
  maxFileSize: 200 * 1024 * 1024, // 200MB
  allowedFileTypes: ['.pdf', '.doc', '.docx'],
};


