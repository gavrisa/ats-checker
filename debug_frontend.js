// Debug script to test frontend-backend connection
console.log('=== ATS Resume Checker Debug ===');

// Test API connection
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => {
    console.log('✅ Backend Health Check:', data);
    
    // Test analyze endpoint
    const formData = new FormData();
    const testFile = new File(['John Doe\nSoftware Engineer\n5 years experience\nJavaScript, React, Node.js'], 'test.txt', { type: 'text/plain' });
    formData.append('resume_file', testFile);
    formData.append('job_description', 'We are looking for a Software Engineer with 5+ years experience in JavaScript and React.');
    
    return fetch('http://localhost:8000/analyze', {
      method: 'POST',
      body: formData
    });
  })
  .then(response => {
    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));
    return response.json();
  })
  .then(data => {
    console.log('✅ Analyze Response:', data);
    console.log('Score:', data.score);
    console.log('Similarity:', data.textSimilarity);
    console.log('Coverage:', data.keywordCoverage);
    console.log('Keywords:', data.all_keywords?.length);
    console.log('Matched:', data.matched_keywords?.length);
    console.log('Missing:', data.missing_keywords?.length);
    console.log('Bullets:', data.bullet_suggestions?.length);
  })
  .catch(error => {
    console.error('❌ Error:', error);
  });

