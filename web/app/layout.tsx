import './globals.css'
import type { Metadata } from 'next'
import { IBM_Plex_Sans_Condensed, Inter, Poppins, Roboto } from 'next/font/google'

// IBM Plex Sans Condensed from Google Fonts
const ibmPlexCondensed = IBM_Plex_Sans_Condensed({
  weight: ['200'], // Extra Light
  subsets: ['latin'],
  variable: '--font-ibm-plex-condensed',
  display: 'swap',
})

// Other custom font configurations
const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const poppins = Poppins({ 
  weight: ['300', '400', '500', '600', '700', '800'],
  subsets: ['latin'],
  variable: '--font-poppins',
  display: 'swap',
})

const roboto = Roboto({ 
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  variable: '--font-roboto',
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
      <body className={`${ibmPlexCondensed.variable} ${inter.variable} ${poppins.variable} ${roboto.variable} font-ibm-condensed font-sans`}>
        {children}
      </body>
    </html>
  )
}
