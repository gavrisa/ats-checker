import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'What is ATS? (and why my CV got rejected the first time)',
  description: 'Plain-English explanation of Applicant Tracking Systems (ATS) with a short personal story and a practical way to check if your CV is ATS-ready.',
  openGraph: {
    title: 'What is ATS? (and why my CV got rejected the first time)',
    description: 'Plain-English explanation of Applicant Tracking Systems (ATS) with a short personal story and a practical way to check if your CV is ATS-ready.',
    type: 'website',
  },
  twitter: {
    card: 'summary',
    title: 'What is ATS? (and why my CV got rejected the first time)',
    description: 'Plain-English explanation of Applicant Tracking Systems (ATS) with a short personal story and a practical way to check if your CV is ATS-ready.',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function WhatIsATSLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}

