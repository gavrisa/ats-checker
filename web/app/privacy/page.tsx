'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';

export default function PrivacyPolicy() {
  const router = useRouter();
  const [screenWidth, setScreenWidth] = useState(0);

  useEffect(() => {
    const updateScreenWidth = () => {
      setScreenWidth(window.innerWidth);
    };

    updateScreenWidth();
    window.addEventListener('resize', updateScreenWidth);
    return () => window.removeEventListener('resize', updateScreenWidth);
  }, []);

  const handleBackClick = () => {
    router.push('/');
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#F2F2F2' }}>


      {/* Main Content Area - Fixed Height */}
      <div className="flex-1 min-h-0 flex flex-col">
        {/* Fixed Header Section */}
        <div 
          className="flex-shrink-0"
          style={{
            display: 'flex',
            padding: 'clamp(1.5rem, 4vh, 2.5rem) clamp(2rem, 5vw, 5.625rem) 0 clamp(2rem, 5vw, 5.625rem)',
            flexDirection: 'column',
            alignItems: 'flex-start',
            gap: 'clamp(1.5rem, 3vh, 2.5rem)'
          }}
        >
          {/* Back Button */}
          <button
            onClick={handleBackClick}
            className="flex items-center gap-3 font-ibm-condensed font-extralight text-black hover:text-gray-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
            style={{
              fontSize: 'clamp(0.875rem, 2vw, 1rem)'
            }}
          >
            <ArrowLeft className="h-5 w-5" />
            Back to Resume Analyzer
          </button>

          {/* Heading */}
          <h1 
            className="font-ibm-condensed font-extralight text-black"
            style={{
              fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
              marginBottom: 'clamp(1.5rem, 3vh, 2rem)' // 24px spacing to first text block
            }}
          >
            Privacy Policy
          </h1>
        </div>

        {/* Scrollable Content Container */}
        <div 
          className="flex-1 min-h-0 overflow-y-auto"
          style={{
            padding: '0 clamp(2rem, 5vw, 5.625rem) clamp(2rem, 4vh, 3rem) clamp(2rem, 5vw, 5.625rem)'
          }}
        >
          <div className="w-full max-w-4xl">
            {/* Content */}
            <div 
              className="font-ibm-condensed font-extralight text-black space-y-4"
              style={{
                fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                lineHeight: '1.6'
              }}
            >
              {/* Section 1 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  1. Resume Uploads
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>When you upload a resume, the file is processed entirely in memory.</li>
                  <li>Files are never stored, written to disk, or logged.</li>
                  <li>The content exists only during analysis and is immediately discarded afterwards.</li>
                </ul>
              </div>

              {/* Section 2 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  2. Job Descriptions
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Job descriptions are processed only to calculate the ATS score.</li>
                  <li>They are not stored, shared, or used for any other purpose.</li>
                </ul>
              </div>

              {/* Section 3 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  3. Other Data
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>We do not collect any personal data.</li>
                  <li>Only standard hosting/analytics data may be collected automatically by our hosting provider (Render/Vercel) and by internal monitoring tools for site performance.</li>
                </ul>
              </div>

              {/* Section 4 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  4. Scope
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>This tool is offered worldwide, free of charge, and intended primarily for personal use.</li>
                  <li>It is a side project built for fun and learning, but made public in case others find it useful too.</li>
                </ul>
              </div>

              {/* Section 5 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  5. Third Parties
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>No data is shared, sold, or transferred to third parties.</li>
                  <li>We do not use advertising, tracking pixels, or external analytics beyond what our hosting provider collects.</li>
                </ul>
              </div>

              {/* Section 6 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  6. Consent
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>By clicking "Get My Score" and using this tool, you agree to this Privacy Policy.</li>
                </ul>
              </div>

              {/* Section 7 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  7. Contact
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>If you have any questions about this Privacy Policy, please contact: <a href="mailto:kate.gavrisa@gmail.com" className="text-blue-600 hover:underline">kate.gavrisa@gmail.com</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer 
        className="w-full border-t border-gray-200 flex-shrink-0"
        style={{
          height: 'clamp(2rem, 2.5vw, 2.5rem)', // 40px on 1920px, scales down
          minHeight: '2rem',
          backgroundColor: '#F2F2F2'
        }}
      >
        <div className="flex items-center justify-between h-full px-6">
          {/* Left side - Copyright */}
          <div 
            className="font-ibm-condensed font-extralight text-black"
            style={{
              fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
            }}
          >
            © 2025 | All rights reserved
          </div>
          
          {/* Right side - Links */}
          <div className="flex items-center gap-6">
            <a 
              href="/faq" 
              className="font-ibm-condensed font-extralight text-black hover:underline transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              style={{
                fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
              }}
            >
              FAQ
            </a>
            <a 
              href="/privacy" 
              className="font-ibm-condensed font-extralight text-black hover:underline transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              style={{
                fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
              }}
            >
              Privacy Policy
            </a>
            <a 
              href="/terms" 
              className="font-ibm-condensed font-extralight text-black hover:underline transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              style={{
                fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
              }}
            >
              Terms & Conditions
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
