import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const FLOW_STEPS = [
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="2" y1="12" x2="22" y2="12"></line>
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
      </svg>
    ),
    title: '1. Provide a Course URL',
    desc: 'Paste the link to any supported course track (like a Binance Academy track). CourseSync will instantly begin mapping the entire curriculum.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 12h20"></path>
        <path d="M12 2v20"></path>
        <path d="m4.9 4.9 14.2 14.2"></path>
        <path d="m4.9 19.1 14.2-14.2"></path>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>
    ),
    title: '2. AI Discovery & Scraping',
    desc: 'Using Firecrawl, we bypass blocks and extract pristine markdown from every module and lesson, automatically filtering out noise.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
        <line x1="12" y1="22.08" x2="12" y2="12"></line>
      </svg>
    ),
    title: '3. LLM Structuring',
    desc: 'An advanced Large Language Model analyzes each scraped page to clean it up, extract metadata, and classify it as a lecture, quiz, or reading.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 22h14a2 2 0 0 0 2-2V7.5L14.5 2H6a2 2 0 0 0-2 2v4"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <path d="M2 15h10"></path>
        <path d="m9 18 3-3-3-3"></path>
      </svg>
    ),
    title: '4. NotebookLM Ready',
    desc: 'Export cleanly organized, logically separated Markdown files that you can directly drag and drop into Google NotebookLM to build a personal AI tutor.',
  }
];

export default function LandingPage() {
  const navigate = useNavigate();
  const cursorRef = useRef<HTMLDivElement>(null);
  const [hovering, setHovering] = useState(false);

  // Custom Cursor Logic
  useEffect(() => {
    document.body.classList.add('landing-page');

    const handleMouseMove = (e: MouseEvent) => {
      if (cursorRef.current) {
        cursorRef.current.style.left = `${e.clientX}px`;
        cursorRef.current.style.top = `${e.clientY}px`;
      }
    };

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName.toLowerCase() === 'button' || target.tagName.toLowerCase() === 'a' || target.closest('button') || target.closest('a')) {
        setHovering(true);
      } else {
        setHovering(false);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseover', handleMouseOver);

    // Flow Step Intersection Observer
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.2 }
    );

    document.querySelectorAll('.flow-step').forEach((el) => {
      observer.observe(el);
    });

    return () => {
      document.body.classList.remove('landing-page');
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseover', handleMouseOver);
      observer.disconnect();
    };
  }, []);

  return (
    <div className="landing-container">
      <div ref={cursorRef} className={`custom-cursor ${hovering ? 'hovering' : ''}`} />
      
      {/* Abstract Background Shapes Removed for solid industrial look */}

      {/* Hero Section */}
      <section className="landing-hero">
        <h1 className="landing-title">
          Turn any course into NotebookLM knowledge in seconds.
        </h1>
        <p className="landing-subtitle">
          CourseSync automatically crawls, extracts, and uses AI to perfectly structure online course materials so you can build your personal AI tutor instantly.
        </p>
        <div className="landing-cta">
          <button 
            className="landing-btn"
            onClick={() => navigate('/dashboard')}
          >
            Get Started
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </div>
      </section>

      {/* Flow Section */}
      <section className="landing-flow">
        {FLOW_STEPS.map((step, index) => (
          <div key={index} className="flow-step">
            <div className="flow-step-icon">{step.icon}</div>
            <div className="flow-step-content">
              <div className="flow-step-title">{step.title}</div>
              <div className="flow-step-desc">{step.desc}</div>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
