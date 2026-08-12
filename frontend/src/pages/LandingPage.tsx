import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import HeroGraphic from './HeroGraphic';

const HOW_IT_WORKS = [
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
      </svg>
    ),
    title: '1. Add Course Link',
    desc: 'Paste any course URL. CourseSync maps the entire curriculum.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <circle cx="10" cy="13" r="2"></circle>
        <line x1="11.5" y1="14.5" x2="14" y2="17"></line>
      </svg>
    ),
    title: '2. AI Extraction',
    desc: 'We crawl and extract lectures, notes, quizzes, and resources.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path>
      </svg>
    ),
    title: '3. AI Structuring',
    desc: 'Nemotron AI structures content into clean, organized knowledge.',
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
    ),
    title: '4. Export & Learn',
    desc: 'Get NotebookLM-ready files and build your personal AI tutor.',
  }
];

const FEATURES = [
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
      </svg>
    ),
    title: 'AI That Understands',
    desc: 'Advanced AI understands context, topics, and concepts with high accuracy.',
    color: '#8b5cf6'
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
      </svg>
    ),
    title: 'Organized & Clean',
    desc: 'Every module, topic, and resource is neatly structured and easy to navigate.',
    color: '#f59e0b'
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
      </svg>
    ),
    title: 'Private by Design',
    desc: 'Your data and courses are never shared. 100% secure and private.',
    color: '#10b981'
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="16" y1="13" x2="8" y2="13"></line>
        <line x1="16" y1="17" x2="8" y2="17"></line>
        <polyline points="10 9 9 9 8 9"></polyline>
      </svg>
    ),
    title: 'NotebookLM Ready',
    desc: 'Export in optimized formats designed for seamless import into NotebookLM.',
    color: '#3b82f6'
  }
];

export default function LandingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    document.body.classList.add('landing-page');
    return () => {
      document.body.classList.remove('landing-page');
    };
  }, []);

  return (
    <div className="landing-container">
      {/* Navbar */}
      <nav className="landing-nav">
        <div className="landing-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path>
          </svg>
          <span style={{fontWeight: 700, fontSize: '20px'}}>CourseSync</span>
        </div>
        <div className="landing-nav-links">
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#students">For Students</a>
          <a href="#pricing">Pricing</a>
          <a href="#docs">Docs</a>
        </div>
        <div className="landing-nav-actions">
          <button className="landing-btn-text" onClick={() => navigate('/dashboard')}>Sign in</button>
          <button className="landing-btn-small" onClick={() => navigate('/dashboard')}>Get Started Free &rarr;</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path></svg>
            AI-Powered Course Intelligence
          </div>
          <h1 className="hero-title">
            Turn any course<br />
            into <span className="hero-highlight">knowledge</span><br />
            <span className="hero-highlight-pink">in seconds.</span>
          </h1>
          <p className="hero-subtitle">
            CourseSync crawls, extracts, and uses AI to<br />
            structure online course materials—so you can<br />
            learn faster and build your personal AI tutor.
          </p>
          <div className="hero-actions">
            <button className="landing-btn" onClick={() => navigate('/dashboard')}>Get Started Free &rarr;</button>
            <button className="landing-btn-outline" onClick={() => navigate('/dashboard')}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16 10 8"></polygon></svg>
              See How It Works
            </button>
          </div>
          
          <div className="hero-tags">
            <span className="hero-tag"><span className="tag-icon" style={{color: '#c084fc'}}>✨</span> AI Structured</span>
            <span className="hero-tag"><span className="tag-icon" style={{color: '#fcd34d'}}>⚡</span> Fast & Accurate</span>
            <span className="hero-tag"><span className="tag-icon" style={{color: '#f472b6'}}>📄</span> NotebookLM Ready</span>
            <span className="hero-tag"><span className="tag-icon" style={{color: '#4ade80'}}>🛡️</span> 100% Private</span>
          </div>
        </div>
        <div className="hero-graphic">
          <HeroGraphic />
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section" id="how-it-works">
        <h3 className="section-label">HOW IT WORKS</h3>
        <h2 className="section-title">From course link to AI knowledge base in 4 simple steps</h2>
        
        <div className="steps-container">
          {HOW_IT_WORKS.map((step, index) => (
            <React.Fragment key={index}>
              <div className="step-card">
                <div className="step-icon-box">{step.icon}</div>
                <div className="step-title">{step.title}</div>
                <div className="step-desc">{step.desc}</div>
              </div>
              {index < HOW_IT_WORKS.length - 1 && (
                <div className="step-arrow">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <div className="features-graphic">
          <div style={{ position: 'relative', mixBlendMode: 'screen' }}>
            <img src="/book-graphic.png" alt="Magic Book" className="floating-img-slow" />
          </div>
        </div>
        <div className="features-content">
          <h2 className="features-headline">
            All your course content.<br />
            <span className="text-purple">Structured.</span> <span className="text-blue">Connected.</span> <span className="text-green">Ready to learn.</span>
          </h2>
          <div className="features-grid">
            {FEATURES.map((feat, i) => (
              <div key={i} className="feature-item">
                <div className="feature-icon" style={{ color: feat.color, backgroundColor: `${feat.color}15` }}>
                  {feat.icon}
                </div>
                <div className="feature-text">
                  <div className="feature-title">{feat.title}</div>
                  <div className="feature-desc">{feat.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="cta-section">
        <div className="cta-box">
          <div className="cta-icon">✨</div>
          <h2 className="cta-title">Start building your AI tutor today</h2>
          <p className="cta-desc">Save hours. Learn better. Stay ahead.</p>
          <button className="landing-btn" onClick={() => navigate('/dashboard')}>Get Started Free &rarr;</button>
        </div>
      </section>
    </div>
  );
}
