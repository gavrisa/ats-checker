import './globals.css'
import type { Metadata } from 'next'
import { IBM_Plex_Sans_Condensed } from 'next/font/google'

// IBM Plex Sans Condensed from Google Fonts
const ibmPlexCondensed = IBM_Plex_Sans_Condensed({
  weight: ['200', '300', '500'], // Extra Light, Light, Medium
  subsets: ['latin'],
  variable: '--font-ibm-plex-condensed',
  display: 'swap',
})

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
      <body className={`${ibmPlexCondensed.variable} font-ibm-condensed font-sans`}>
        {children}
      </body>
    </html>
  )
}
