import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ATS Resume Checker',
  description: 'Check your resume against job descriptions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
