import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ATS Resume Checker',
  description: 'Check how your resume matches any job description. Get missing keywords, smart bullets, and a clear path to 100% coverage.',
  keywords: 'ATS, resume, job application, keyword optimization, resume checker',
  authors: [{ name: 'ATS Resume Checker Team' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
