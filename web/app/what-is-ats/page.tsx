'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function WhatIsATS() {
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

  // Analytics tracking
  useEffect(() => {
    // Fire page view event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'page_view', {
        page_name: 'what_is_ats'
      });
    }
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

  const handleCheckCVClick = () => {
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
            What is ATS? (and why my CV got rejected the first time)
          </h1>
        </div>

        {/* Scrollable Content Container */}
        <div 
          className="flex-1 min-h-0 overflow-y-auto"
          style={{
            padding: '0 clamp(2rem, 5vw, 5.625rem) clamp(2rem, 4vh, 3rem) clamp(2rem, 5vw, 5.625rem)'
          }}
        >
          <div className="max-w-4xl">
            {/* Intro Paragraphs */}
            <div className="mb-8">
              <p 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                When I first heard the term ATS, I thought it was some kind of new design framework.
              </p>
              <p 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                Turns out, it's a piece of software that decides whether your CV reaches a recruiter or goes straight into the digital void.
              </p>
              <p 
                className="font-ibm-condensed font-extralight text-black"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                And yes, my first CV didn't make it through.
              </p>
            </div>

            {/* So, what exactly is ATS? */}
            <div className="mb-8">
              <h2 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
                  lineHeight: '1.4'
                }}
              >
                So, what exactly is ATS?
              </h2>
              <p 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                ATS = Applicant Tracking System.
              </p>
              <p 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                It's software that recruiters and HR teams use to:
              </p>
              <ul className="list-disc list-inside mb-4 ml-4">
                <li 
                  className="font-ibm-condensed font-extralight text-black mb-2"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                    lineHeight: '1.4'
                  }}
                >
                  collect and organize hundreds of CVs in one place
                </li>
                <li 
                  className="font-ibm-condensed font-extralight text-black mb-2"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                    lineHeight: '1.4'
                  }}
                >
                  automatically filter candidates
                </li>
                <li 
                  className="font-ibm-condensed font-extralight text-black mb-2"
                  style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                    lineHeight: '1.4'
                  }}
                >
                  scan for keywords that match the job description
                </li>
              </ul>
              <p 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                If your CV contains the right words, you have a chance of landing on a recruiter's desk.
              </p>
              <p 
                className="font-ibm-condensed font-extralight text-black"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                If not, it often never gets seen by a human.
              </p>
            </div>

            {/* A real example */}
            <div className="mb-8">
              <h2 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
                  lineHeight: '1.4'
                }}
              >
                A real example
              </h2>
              <p 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                The job description asks for: Figma, prototyping, user testing.
              </p>
              <p 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                Your CV only says: design tools, testing ideas.
              </p>
              <p 
                className="font-ibm-condensed font-extralight text-black"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                For the ATS, that's not a match. The system doesn't guess—it just looks for exact keywords.
              </p>
            </div>

            {/* Why it matters */}
            <div className="mb-8">
              <h2 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
                  lineHeight: '1.4'
                }}
              >
                Why it matters
              </h2>
              <p 
                className="font-ibm-condensed font-extralight text-black"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                Because around 90% of medium and large companies use an ATS.
              </p>
              <p 
                className="font-ibm-condensed font-extralight text-black mt-4"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                If your CV isn't optimized for it, you can lose the opportunity before the recruiter even sees your name.
              </p>
            </div>

            {/* The good news */}
            <div className="mb-8">
              <h2 
                className="font-ibm-condensed font-extralight text-black mb-4"
                style={{
                  fontSize: 'clamp(1.25rem, 3vw, 1.5rem)',
                  lineHeight: '1.4'
                }}
              >
                The good news
              </h2>
              <p 
                className="font-ibm-condensed font-extralight text-black mb-6"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  lineHeight: '1.4'
                }}
              >
                I built an ATS-checker to help with this. It scans your CV against a job description and shows which keywords you're missing—so the next time, your CV gets through.
              </p>
              
              {/* CTA Button */}
              <button
                onClick={handleCheckCVClick}
                className="font-ibm-condensed font-extralight text-white bg-black hover:bg-gray-800 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
                style={{
                  fontSize: 'clamp(1rem, 2.5vw, 1.125rem)',
                  padding: 'clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 4vw, 2rem)',
                  borderRadius: '4px'
                }}
              >
                Check my CV
              </button>
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
