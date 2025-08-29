# ATS Resume Checker

A modern, production-ready web application for analyzing resume compatibility with job descriptions using AI-powered keyword analysis and smart suggestions.

## 🎯 What It Does

- **Resume Analysis**: Upload your resume (PDF, DOCX, TXT) and paste any job description
- **ATS Optimization**: Get an ATS match score (0-100) with detailed breakdown
- **Keyword Coverage**: See which job keywords are present vs missing in your resume
- **Smart Bullets**: Get contextual bullet point suggestions to improve your score
- **Real-time Feedback**: Instant analysis with beautiful, animated visualizations

## 🏗️ Architecture

```
ats_checker_mvp/
├── api/                    # FastAPI Backend
│   ├── main.py            # API endpoints and logic
│   ├── schemas.py          # Pydantic models
│   └── requirements.txt    # Python dependencies
├── web/                    # Next.js Frontend
│   ├── app/               # Next.js App Router
│   ├── components/        # React components
│   ├── package.json       # Node.js dependencies
│   └── README.md          # Frontend documentation
├── utils.py               # Core analysis functions
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Backend (FastAPI)

```bash
# Navigate to API directory
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py
```

**API will be available at:** `http://localhost:8000`

### 2. Frontend (Next.js)

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

**Frontend will be available at:** `http://localhost:3000`

## 🎨 Features

### ✨ Modern UI/UX
- **Split-screen layout**: Left panel for inputs, right panel for results
- **Responsive design**: Works perfectly on all devices
- **Smooth animations**: Framer Motion powered interactions
- **Professional styling**: Tailwind CSS with custom design system

### 🔍 Smart Analysis
- **Keyword extraction**: Top 30 relevant keywords from job descriptions
- **Coverage calculation**: Percentage of keywords found in resume
- **Text similarity**: TF-IDF cosine similarity analysis
- **ATS scoring**: Weighted algorithm (70% keywords + 30% similarity)

### 📊 Visual Results
- **Score display**: Large, animated score with color coding
- **Progress bars**: Animated bars for all metrics
- **Keyword chips**: Visual breakdown of present vs missing keywords
- **Bullet suggestions**: Contextual recommendations with copy functionality

### 🛡️ Production Ready
- **Error handling**: Comprehensive error states and validation
- **File validation**: Type, size, and content checking
- **CORS configuration**: Secure API communication
- **Deployment ready**: Vercel (frontend) + Render (backend) compatible

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **Pydantic**: Data validation and serialization
- **Python-docx**: DOCX file processing
- **PyPDF2**: PDF text extraction
- **Scikit-learn**: TF-IDF similarity calculations

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Lucide React**: Beautiful icon set

## 📱 Responsive Design

- **Mobile**: Single column, stacked layout
- **Tablet**: Two column layout
- **Desktop**: Three column layout (1:2 ratio)
- **Container**: Max-width 1280px with proper margins

## 🚀 Deployment

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set environment variable: `NEXT_PUBLIC_API_URL`
3. Deploy automatically on push to main

### Backend (Render)
1. Connect GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python main.py`
4. Deploy as web service

## 🔧 Development

### Prerequisites
- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git** for version control

### Local Development
1. **Clone repository**
2. **Start backend**: `cd api && python main.py`
3. **Start frontend**: `cd web && npm run dev`
4. **Open browser**: Navigate to `http://localhost:3000`

### Environment Variables
```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend (optional)
CORS_ORIGINS=http://localhost:3000,https://your-domain.vercel.app
```

## 📊 API Endpoints

### `POST /analyze`
Analyze resume compatibility with job description.

**Request:**
- `resume_file`: File upload (PDF, DOCX, TXT)
- `job_description`: Text string (min 50 chars)

**Response:**
```json
{
  "score": 75,
  "textSimilarity": 68.5,
  "keywordCoverage": 76.7,
  "jdKeywordsTop30": ["design", "user", "experience", ...],
  "present": ["design", "user", ...],
  "missing": ["experience", "prototyping", ...],
  "bullets": ["Led design initiatives...", ...],
  "analysis": {
    "resumeWords": 1250,
    "jdWords": 890,
    "keywordsFound": 23,
    "keywordsMissing": 7,
    "totalKeywords": 30
  }
}
```

### `GET /health`
Health check endpoint.

### `GET /`
API information and documentation.

## 🎯 Use Cases

- **Job Seekers**: Optimize resumes for specific positions
- **Recruiters**: Validate resume-job description matches
- **HR Teams**: Standardize resume screening processes
- **Career Coaches**: Provide data-driven resume feedback
- **Students**: Learn ATS optimization best practices

## 🔒 Security Features

- **File validation**: Type, size, and content checking
- **Input sanitization**: XSS prevention
- **CORS protection**: Configurable origin restrictions
- **Error handling**: Secure error messages
- **Rate limiting**: Built-in protection (configurable)

## 📈 Performance

- **Fast analysis**: Optimized algorithms for quick results
- **Efficient processing**: Minimal memory usage
- **Caching**: Built-in response caching
- **Async operations**: Non-blocking API calls
- **Optimized builds**: Production-ready frontend builds

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Create GitHub issue with detailed description
- **Documentation**: Check `/web/README.md` for frontend details
- **API Docs**: Visit `http://localhost:8000/docs` when backend is running

## 🙏 Acknowledgments

- **FastAPI** team for the excellent Python framework
- **Vercel** for seamless frontend deployment
- **Tailwind CSS** for the utility-first CSS framework
- **Framer Motion** for beautiful animations

---

**Built with ❤️ using modern web technologies**

*Optimize your resume for ATS systems and land your dream job!*