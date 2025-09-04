import fetch from 'node-fetch';
import FormData from 'form-data';
import fs from 'fs';

const API_BASE = 'https://ats-checker-cz1i.onrender.com';

async function testHealth() {
    console.log('🔍 Testing health endpoint...');
    try {
        const response = await fetch(`${API_BASE}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'ATS-Checker-Debug/1.0'
            }
        });
        
        console.log(`📊 Health response status: ${response.status}`);
        console.log(`📋 Health response headers:`, Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Health test successful:', data);
            return true;
        } else {
            const text = await response.text();
            console.log('❌ Health test failed:', text);
            return false;
        }
    } catch (error) {
        console.log('❌ Health test error:', error.message);
        return false;
    }
}

async function testAnalyze() {
    console.log('\n🔍 Testing analyze endpoint...');
    try {
        // Create a simple test file
        const testContent = 'Software Engineer with 5 years of experience in Python, JavaScript, and React.';
        fs.writeFileSync('test_resume_debug.txt', testContent);
        
        const formData = new FormData();
        formData.append('resume_file', fs.createReadStream('test_resume_debug.txt'));
        formData.append('job_description', 'Software Engineer position requiring Python, JavaScript, and React experience.');
        
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'ATS-Checker-Debug/1.0',
                ...formData.getHeaders()
            }
        });
        
        console.log(`📊 Analyze response status: ${response.status}`);
        console.log(`📋 Analyze response headers:`, Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Analyze test successful:', JSON.stringify(data, null, 2));
            return true;
        } else {
            const text = await response.text();
            console.log('❌ Analyze test failed:', text);
            return false;
        }
    } catch (error) {
        console.log('❌ Analyze test error:', error.message);
        return false;
    } finally {
        // Clean up test file
        if (fs.existsSync('test_resume_debug.txt')) {
            fs.unlinkSync('test_resume_debug.txt');
        }
    }
}

async function runTests() {
    console.log('🚀 Starting API tests...\n');
    
    const healthOk = await testHealth();
    const analyzeOk = await testAnalyze();
    
    console.log('\n📈 Test Results:');
    console.log(`Health endpoint: ${healthOk ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Analyze endpoint: ${analyzeOk ? '✅ PASS' : '❌ FAIL'}`);
    
    if (healthOk && analyzeOk) {
        console.log('\n🎉 All tests passed! The API is working correctly.');
        console.log('The issue might be in the frontend or browser environment.');
    } else {
        console.log('\n⚠️  Some tests failed. Check the API deployment.');
    }
}

// Run the tests
runTests().catch(console.error);
