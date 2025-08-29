# ATS Resume Checker - Frontend

A modern, responsive web application built with Next.js 14, TypeScript, and Tailwind CSS for analyzing resume compatibility with job descriptions.

## 🚀 Features

- **Modern UI/UX**: Clean, professional design with smooth animations
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Real-time Analysis**: Instant feedback on resume-job description matching
- **Interactive Components**: Drag & drop file upload, animated progress bars
- **Smart Suggestions**: Contextual bullet point recommendations
- **Keyword Analysis**: Visual breakdown of present vs missing keywords

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **State Management**: React Hooks
- **API Integration**: Fetch API

## 📁 Project Structure

```
web/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main page
├── components/             # Reusable components
│   ├── FileUploader.tsx   # Drag & drop file upload
│   ├── JDTextArea.tsx     # Job description input
│   ├── ScoreCard.tsx      # ATS score display
│   ├── KeywordChips.tsx   # Keyword visualization
│   └── BulletSuggestions.tsx # Smart bullet points
├── package.json           # Dependencies
├── tailwind.config.js     # Tailwind configuration
├── tsconfig.json          # TypeScript configuration
└── next.config.js         # Next.js configuration
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running (see `/api` directory)

### Installation

1. **Install dependencies**:
   ```bash
   cd web
   npm install
   ```

2. **Set up environment variables**:
   Create `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open browser**:
   Navigate to `http://localhost:3000`

## 🎨 Design System

### Colors
- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Neutral**: Gray scale

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: 16px - 48px
- **Body**: 14px - 16px
- **Captions**: 12px - 14px

### Spacing
- **Container**: Max-width 1280px
- **Margins**: 32px - 48px
- **Padding**: 16px - 24px
- **Border Radius**: 16px - 24px

### Animations
- **Duration**: 200ms - 800ms
- **Easing**: Ease-out, Spring
- **Transitions**: Opacity, Scale, Transform

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Component Development

Each component follows these principles:
- **TypeScript interfaces** for props
- **Framer Motion** for animations
- **Tailwind CSS** for styling
- **Responsive design** by default
- **Accessibility** considerations

### State Management

- **Local State**: React useState for component state
- **Form State**: Controlled inputs with validation
- **API State**: Loading, success, error states
- **File State**: File upload and validation

## 🌐 API Integration

### Endpoints

- `POST /analyze` - Analyze resume with job description
- `GET /health` - Health check
- `GET /` - API information

### Request Format

```typescript
interface AnalysisRequest {
  resume_file: File;
  job_description: string;
}
```

### Response Format

```typescript
interface AnalysisResponse {
  score: number;
  textSimilarity: number;
  keywordCoverage: number;
  jdKeywordsTop30: string[];
  present: string[];
  missing: string[];
  bullets: string[];
  analysis: {
    resumeWords: number;
    jdWords: number;
    keywordsFound: number;
    keywordsMissing: number;
    totalKeywords: number;
  };
}
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Layout
- **Mobile**: Single column, stacked layout
- **Tablet**: Two column layout
- **Desktop**: Three column layout (1:2 ratio)

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect repository** to Vercel
2. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL
3. **Deploy** automatically on push to main branch

### Other Platforms

- **Netlify**: Compatible with Next.js
- **Railway**: Full-stack deployment
- **Render**: Static site hosting

## 🔒 Security

- **File Validation**: Type and size checking
- **Input Sanitization**: XSS prevention
- **CORS Configuration**: Backend API protection
- **Environment Variables**: Secure configuration

## 📊 Performance

- **Code Splitting**: Automatic by Next.js
- **Image Optimization**: Built-in optimization
- **Bundle Analysis**: Webpack bundle analyzer
- **Lighthouse**: Performance monitoring

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch
3. **Make** changes with tests
4. **Submit** pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check existing issues
- Create new issue with details
- Contact development team

---

Built with ❤️ using Next.js, TypeScript, and Tailwind CSS
