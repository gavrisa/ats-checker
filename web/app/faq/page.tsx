'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, ChevronDown, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface FAQItem {
  id: string;
  question: string;
  answer: string;
}

export default function FAQ() {
  const router = useRouter();
  const [screenWidth, setScreenWidth] = useState(0);
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());
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

  const toggleItem = (itemId: string) => {
    setOpenItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const handleKeyDown = (event: React.KeyboardEvent, itemId: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleItem(itemId);
    }
  };

  const faqItems: FAQItem[] = [
    {
      id: 'what-is-tool',
      question: 'What is this tool?',
      answer: "It's a resume analyzer that checks how well your CV matches a specific job description. It shows missing keywords, smart bullet suggestions, and an overall ATS score."
    },
    {
      id: 'store-data',
      question: 'Do you store my resume or job description?',
      answer: 'No. Resumes and job descriptions are processed only in memory and are discarded right after analysis. We don\'t save or share your files.'
    },
    {
      id: 'data-safe',
      question: 'Is my data safe?',
      answer: 'Yes. We don\'t keep or sell personal data. Only standard technical logs may be collected automatically by our hosting provider (Render/Vercel) for site performance.'
    },
    {
      id: 'ats-guarantee',
      question: 'Does the ATS score guarantee I\'ll get the job?',
      answer: 'No. The score is guidance to optimize your resume for ATS. Hiring decisions also depend on interviews, skills, and team fit.'
    },
    {
      id: 'who-for',
      question: 'Who is this tool for?',
      answer: 'Anyone applying for jobs — especially designers/developers in tech. It\'s free and available worldwide.'
    },
    {
      id: 'why-built',
      question: 'Why did you build it?',
      answer: 'It\'s a personal side project built for fun and for my own use, made public in case others find it helpful.'
    },
    {
      id: 'who-built',
      question: 'Who built this tool / how can I contact you?',
      answer: 'Built by Jekaterina Gavrisa. Contact: kate.gavrisa@gmail.com'
    }
  ];

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
            FAQ
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
            {/* FAQ Items */}
            <div 
              className="space-y-2"
              style={{
                fontSize: 'clamp(0.875rem, 2vw, 1rem)',
                lineHeight: '1.6',
                padding: '8px 0' // Add padding to ensure focus border is visible
              }}
            >
              {faqItems.map((item, index) => {
                const isOpen = openItems.has(item.id);
                
                return (
                  <div 
                    key={item.id} 
                    className="transition-all duration-200"
                    style={{
                      backgroundColor: '#F2F2F2',
                      borderBottom: '1px solid #E0E0E0',
                      margin: '4px 0' // Add margin to ensure focus border is visible
                    }}
                  >
                    {/* Question Button */}
                    <button
                      onClick={() => toggleItem(item.id)}
                      onKeyDown={(e) => handleKeyDown(e, item.id)}
                      className="w-full text-left flex items-center justify-between p-4 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-4 hover:bg-gray-50 transition-colors duration-200"
                      style={{
                        backgroundColor: 'transparent',
                        borderRadius: '0'
                      }}
                      aria-expanded={isOpen}
                      aria-controls={`answer-${item.id}`}
                    >
                      <h2 
                        className="font-ibm-condensed text-black pr-4"
                        style={{
                          fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
                          fontWeight: '500'
                        }}
                      >
                        {item.question}
                      </h2>
                      <ChevronDown 
                        className={`h-5 w-5 text-gray-600 transition-transform duration-200 flex-shrink-0 ${
                          isOpen ? 'rotate-180' : 'rotate-0'
                        }`}
                      />
                    </button>

                    {/* Answer Panel */}
                    <div
                      id={`answer-${item.id}`}
                      className={`overflow-hidden transition-all duration-300 ease-in-out ${
                        isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                      }`}
                      aria-hidden={!isOpen}
                    >
                      <div 
                        className="px-4 pb-4"
                        style={{
                          paddingTop: '12px',
                          backgroundColor: 'transparent'
                        }}
                      >
                        <p 
                          className="font-ibm-condensed font-extralight text-black"
                          style={{
                            fontSize: '16px',
                            lineHeight: '24px'
                          }}
                        >
                          {item.answer}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
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
        <div className="flex items-center justify-center h-full px-6">
          {/* Centered Copyright */}
          <div 
            className="font-ibm-condensed font-extralight text-black"
            style={{
              fontSize: 'clamp(0.75rem, 1.2vw, 0.75rem)' // 12px
            }}
          >
            © 2025 | All rights reserved
          </div>
          
          {/* Desktop Links - Hidden on mobile since burger menu is now in header */}
          <div className="hidden md:flex items-center gap-6 ml-auto">
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
        </div>
      </footer>
    </div>
  );
}
