
import './HeroGraphic.css';

export default function HeroGraphic() {
  return (
    <div className="hero-composition">
      {/* Background glow */}
      <div className="hero-comp-glow"></div>

      {/* Left side floating pills */}
      <div className="hero-comp-pills">
        <div className="comp-pill" style={{ animationDelay: '0s' }}>
          <div className="comp-pill-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg></div>
          <span>Course Link</span>
        </div>
        <div className="comp-pill" style={{ animationDelay: '0.2s' }}>
          <div className="comp-pill-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg></div>
          <span>Lectures</span>
        </div>
        <div className="comp-pill" style={{ animationDelay: '0.4s' }}>
          <div className="comp-pill-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg></div>
          <span>Notes</span>
        </div>
        <div className="comp-pill" style={{ animationDelay: '0.6s' }}>
          <div className="comp-pill-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg></div>
          <span>Quizzes</span>
        </div>
        <div className="comp-pill" style={{ animationDelay: '0.8s' }}>
          <div className="comp-pill-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg></div>
          <span>Resources</span>
        </div>
      </div>

      {/* Center Laptop / Processing UI */}
      <div className="hero-comp-center">
        <div className="comp-laptop">
          <div className="comp-laptop-screen">
            <div className="comp-laptop-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
              <span>AI Structuring...</span>
            </div>
            <div className="comp-laptop-body">
              <div className="comp-task done"><span className="check">✓</span> Extracting content</div>
              <div className="comp-task done"><span className="check">✓</span> Understanding topics</div>
              <div className="comp-task done"><span className="check">✓</span> Organizing knowledge</div>
              <div className="comp-task active"><span className="spinner"></span> Preparing for NotebookLM</div>
              
              <div className="comp-progress">
                <div className="comp-progress-bar" style={{ width: '85%' }}></div>
              </div>
              <div className="comp-progress-text">85%</div>
            </div>
          </div>
          <div className="comp-laptop-base"></div>
        </div>
      </div>

      {/* Right side output card */}
      <div className="hero-comp-output">
        <div className="comp-glass-card">
          <div className="comp-glass-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2"><path d="M4 22h14a2 2 0 0 0 2-2V7.5L14.5 2H6a2 2 0 0 0-2 2v4"></path><polyline points="14 2 14 8 20 8"></polyline><path d="M2 15h10"></path><path d="m9 18 3-3-3-3"></path></svg>
            NotebookLM<br/>Ready
          </div>
          <div className="comp-glass-list">
            <div><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Course Overview</div>
            <div><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Module 01</div>
            <div><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Module 02</div>
            <div><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Quiz Bank</div>
            <div><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Glossary</div>
          </div>
        </div>
      </div>
      
      {/* Connecting lines */}
      <svg className="hero-comp-lines" viewBox="0 0 400 300">
        <path d="M 50 50 Q 200 150 250 150" fill="none" stroke="rgba(168, 85, 247, 0.4)" strokeWidth="2" />
        <path d="M 50 100 Q 200 150 250 150" fill="none" stroke="rgba(168, 85, 247, 0.4)" strokeWidth="2" />
        <path d="M 50 150 Q 200 150 250 150" fill="none" stroke="rgba(168, 85, 247, 0.4)" strokeWidth="2" />
        <path d="M 50 200 Q 200 150 250 150" fill="none" stroke="rgba(168, 85, 247, 0.4)" strokeWidth="2" />
        <path d="M 50 250 Q 200 150 250 150" fill="none" stroke="rgba(168, 85, 247, 0.4)" strokeWidth="2" />
      </svg>
    </div>
  );
}
