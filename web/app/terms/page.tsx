'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function TermsAndConditions() {
  const router = useRouter();
  const [screenWidth, setScreenWidth] = useState(0);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const updateScreenWidth = () => {
      setScreenWidth(window.innerWidth);
    };

    updateScreenWidth();
    window.addEventListener('resize', updateScreenWidth);
    return () => window.removeEventListener('resize', updateScreenWidth);
  }, []);

  // Handle click outside to close mobile menu
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMenuOpen]);

  const handleBackClick = () => {
    router.push('/');
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#F2F2F2' }}>
      {/* Header with Burger Menu */}
      <header className="w-full border-b border-gray-200 flex-shrink-0 md:hidden"
        style={{
          height: 'clamp(3rem, 4vw, 4rem)',
          minHeight: '3rem',
          backgroundColor: '#F2F2F2'
        }}
      >
        <div className="flex items-center justify-end h-full px-6">
          {/* Mobile Burger Menu */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="font-ibm-condensed font-extralight text-black hover:text-gray-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 p-1"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>

            {/* Mobile Menu Dropdown */}
            <AnimatePresence>
              {isMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                  className="absolute top-full right-0 mt-2 bg-white border border-gray-200 rounded-md shadow-lg py-2 min-w-[200px] z-50"
                >
                  <a 
                    href="/what-is-ats" 
                    className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                    style={{ fontSize: '0.875rem' }}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    What is ATS?
                  </a>
                  <a 
                    href="/faq" 
                    className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                    style={{ fontSize: '0.875rem' }}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    FAQ
                  </a>
                  <a 
                    href="/privacy" 
                    className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                    style={{ fontSize: '0.875rem' }}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Privacy Policy
                  </a>
                  <a 
                    href="/terms" 
                    className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                    style={{ fontSize: '0.875rem' }}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Terms & Conditions
                  </a>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>


      {/* Main Content Area - Fixed Height */}
      <div className="flex-1 min-h-0 flex flex-col"
        style={{
          minHeight: 'calc(100vh - clamp(2rem, 2.5vw, 2.5rem) - clamp(3rem, 4vw, 4rem))', // 100vh minus footer and header height
          height: 'calc(100vh - clamp(2rem, 2.5vw, 2.5rem) - clamp(3rem, 4vw, 4rem))',
          overflow: 'hidden'
        }}
      >
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
            Terms & Conditions
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
                  1. Acceptance of Terms
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>By using this tool, you agree to these Terms & Conditions.</li>
                  <li>If you do not agree, please do not use the service.</li>
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
                  2. Purpose of the Tool
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>This tool is provided "as is" for personal use, free of charge.</li>
                  <li>It is intended to help users analyze resumes against job descriptions.</li>
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
                  3. No Guarantees
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>We make no guarantees about the accuracy, completeness, or usefulness of the ATS score or results.</li>
                  <li>The tool is experimental and should not be considered a substitute for professional or legal advice.</li>
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
                  4. User Responsibility
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>You are responsible for the content you upload (resume and job descriptions).</li>
                  <li>Do not upload materials that contain sensitive personal data beyond what is necessary for analysis.</li>
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
                  5. Intellectual Property
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>The code, design, and content of this site remain the intellectual property of the creator.</li>
                  <li>You may not copy, redistribute, or resell the tool without written permission.</li>
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
                  6. Liability
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>We are not liable for any outcomes, losses, or damages arising from the use of this tool.</li>
                  <li>Use of the tool is at your own risk.</li>
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
                  7. Changes to Terms
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>We may update these Terms & Conditions at any time.</li>
                  <li>Continued use of the tool after changes means you accept the updated Terms.</li>
                </ul>
              </div>

              {/* Section 8 */}
              <div>
                <h2 
                  className="font-ibm-condensed font-extralight text-black mb-3"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                    fontWeight: '400'
                  }}
                >
                  8. Contact
                </h2>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>For any questions about these Terms, contact: <a href="mailto:kate.gavrisa@gmail.com" className="text-blue-600 hover:underline">kate.gavrisa@gmail.com</a></li>
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
            {/* Desktop Links */}
            <div className="hidden md:flex items-center gap-6">
              <a 
                href="/what-is-ats" 
                className="font-ibm-condensed font-extralight text-black hover:underline transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
                style={{
                  fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
                }}
              >
                What is ATS?
              </a>
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

            {/* Mobile Burger Menu */}
            <div className="md:hidden relative" ref={menuRef}>
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="font-ibm-condensed font-extralight text-black hover:text-gray-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 p-1"
                aria-label="Toggle menu"
              >
                {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>

              {/* Mobile Menu Dropdown */}
              <AnimatePresence>
                {isMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute bottom-full right-0 mb-2 bg-white border border-gray-200 rounded-md shadow-lg py-2 min-w-[200px] z-50"
                  >
                    <a 
                      href="/what-is-ats" 
                      className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                      style={{ fontSize: '0.875rem' }}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      What is ATS?
                    </a>
                    <a 
                      href="/faq" 
                      className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                      style={{ fontSize: '0.875rem' }}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      FAQ
                    </a>
                    <a 
                      href="/privacy" 
                      className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                      style={{ fontSize: '0.875rem' }}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Privacy Policy
                    </a>
                    <a 
                      href="/terms" 
                      className="block px-4 py-2 font-ibm-condensed font-extralight text-black hover:bg-gray-50 transition-colors duration-200"
                      style={{ fontSize: '0.875rem' }}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Terms & Conditions
                    </a>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
