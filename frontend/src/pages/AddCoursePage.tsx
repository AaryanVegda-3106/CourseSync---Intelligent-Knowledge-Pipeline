import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCourse, discoverCourse } from '../services/api';

export default function AddCoursePage() {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState<'form' | 'discovering'>('form');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!name.trim() || !url.trim()) {
      setError('Course name and URL are required.');
      return;
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setError('URL must start with http:// or https://');
      return;
    }

    setLoading(true);
    setStage('discovering');

    try {
      // Step 1: Create course
      const course = await createCourse({ name: name.trim(), url: url.trim() });

      // Step 2: Run discovery
      await discoverCourse(course.id);

      // Navigate to discovery / course view
      navigate(`/course/${course.id}`);
    } catch (err: any) {
      setError(err.detail || err.message || 'Failed to create course');
      setStage('form');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Add Course</h1>
        <p className="page-subtitle">
          Enter a university course URL to discover its structure and extract content.
        </p>
      </div>

      <div className="card" style={{ maxWidth: 560 }}>
        {stage === 'form' ? (
          <form onSubmit={handleSubmit} id="add-course-form">
            <div className="flex flex-col gap-4">
              <div className="input-group">
                <label className="input-label" htmlFor="course-name">
                  Course Name
                </label>
                <input
                  id="course-name"
                  className="input"
                  type="text"
                  placeholder="e.g. Introduction to Data Science"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={loading}
                  autoFocus
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="course-url">
                  Course URL
                </label>
                <input
                  id="course-url"
                  className="input"
                  type="url"
                  placeholder="https://example.edu/course/data-science"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={loading}
                />
                <span className="text-xs text-muted">
                  The root URL of the course — CourseSync will discover all sub-pages automatically.
                </span>
              </div>

              {error && (
                <div
                  style={{
                    background: 'var(--color-error-muted)',
                    color: 'var(--color-error)',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '13px',
                  }}
                >
                  {error}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  type="submit"
                  className="btn btn-primary btn-lg"
                  disabled={loading}
                  id="btn-discover"
                >
                  Discover Course
                </button>
                <button
                  type="button"
                  className="btn btn-secondary btn-lg"
                  onClick={() => navigate('/dashboard')}
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        ) : (
          <div className="flex flex-col items-center gap-4" style={{ padding: '32px 0' }}>
            <div className="spinner spinner-lg" />
            <div>
              <div className="font-semibold" style={{ textAlign: 'center' }}>
                Discovering course structure…
              </div>
              <div className="text-sm text-muted" style={{ textAlign: 'center', marginTop: 4 }}>
                Mapping URLs and classifying pages. This may take a moment.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
