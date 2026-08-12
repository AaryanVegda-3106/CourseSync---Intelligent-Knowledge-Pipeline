import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const FLOW_STEPS = [
  {
    icon: '🌐',
    title: '1. Provide a Course URL',
    desc: 'Paste the link to any supported course track (like a Binance Academy track). CourseSync will instantly begin mapping the entire curriculum.',
  },
  {
    icon: '🕷️',
    title: '2. AI Discovery & Scraping',
    desc: 'Using Firecrawl, we bypass blocks and extract pristine markdown from every module and lesson, automatically filtering out noise.',
  },
  {
    icon: '🧠',
    title: '3. LLM Structuring',
    desc: 'An advanced Large Language Model analyzes each scraped page to clean it up, extract metadata, and classify it as a lecture, quiz, or reading.',
  },
  {
    icon: '🚀',
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
      
      {/* Abstract Background Shapes */}
      <div className="bg-shape bg-shape-1" />
      <div className="bg-shape bg-shape-2" />

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
          <div key={index} className="flow-step card" style={{ display: 'flex', border: '1px solid rgba(255,255,255,0.1)' }}>
            <div className="flow-step-icon" style={{ background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(147, 51, 234, 0.05))', border: '1px solid rgba(124, 58, 237, 0.3)' }}>{step.icon}</div>
            <div className="flow-step-content">
              <div className="flow-step-title" style={{ color: '#fff' }}>{step.title}</div>
              <div className="flow-step-desc" style={{ color: 'var(--color-text-secondary)' }}>{step.desc}</div>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
