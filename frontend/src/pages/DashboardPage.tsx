import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Course } from '../types';
import { listCourses, deleteCourse } from '../services/api';

const STATUS_BADGE: Record<string, string> = {
  created: 'badge-neutral',
  discovering: 'badge-info',
  discovered: 'badge-accent',
  ingesting: 'badge-info',
  ingested: 'badge-success',
  processing: 'badge-warning',
  processed: 'badge-success',
  exporting: 'badge-warning',
  exported: 'badge-success',
  failed: 'badge-error',
};

export default function DashboardPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadCourses();
  }, []);

  async function loadCourses() {
    try {
      const data = await listCourses();
      setCourses(data.courses);
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this course and all its files?')) {
      return;
    }
    try {
      await deleteCourse(id);
      await loadCourses();
    } catch (err) {
      console.error('Failed to delete course:', err);
      alert('Failed to delete course');
    }
  }

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return '—';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="flex items-center justify-between" style={{ justifyContent: 'center', padding: '80px 0' }}>
          <div className="spinner spinner-lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="page-title">Courses</h1>
          <p className="page-subtitle">{courses.length} course{courses.length !== 1 ? 's' : ''} in your library</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/add')}
          id="btn-add-course"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add Course
        </button>
      </div>

      {courses.length === 0 ? (
        <div className="empty-state card" style={{ padding: '80px 32px' }}>
          <div className="empty-state-icon" style={{ fontSize: '48px', marginBottom: '24px', background: 'transparent' }}>🔭</div>
          <div className="empty-state-title" style={{ fontSize: '20px' }}>Your universe is empty</div>
          <div className="empty-state-description" style={{ fontSize: '15px' }}>
            Add your first course URL to start extracting knowledge and building your AI brain.
          </div>
          <button
            className="btn btn-primary btn-lg mt-6"
            onClick={() => navigate('/add')}
          >
            Add First Course
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px' }}>
          {courses.map(course => (
            <div
              key={course.id}
              className="card flex-col justify-between"
              style={{ cursor: 'pointer', display: 'flex', minHeight: '200px' }}
              onClick={() => {
                if (['discovered', 'ingested', 'processed', 'exported', 'failed'].includes(course.status)) {
                  navigate(`/course/${course.id}`);
                }
              }}
            >
              <div>
                <div className="flex justify-between items-start mb-3">
                  <span className={`badge ${STATUS_BADGE[course.status] || 'badge-neutral'}`}>
                    {course.status}
                  </span>
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ padding: '4px', color: 'var(--color-error)', opacity: 0.6 }}
                    onClick={(e) => handleDelete(e, course.id)}
                    title="Delete Course"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
                <div className="font-semibold" style={{ fontSize: '16px', lineHeight: 1.3, marginBottom: '8px' }}>
                  {course.name}
                </div>
                <div className="text-xs text-muted truncate" style={{ opacity: 0.8 }}>
                  {course.url}
                </div>
              </div>
              
              <div style={{ marginTop: '24px', borderTop: '1px solid var(--color-border)', paddingTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '16px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-tertiary)', textTransform: 'uppercase' }}>Modules</span>
                    <span style={{ fontSize: '14px', fontWeight: 600 }}>{course.module_count}</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-tertiary)', textTransform: 'uppercase' }}>Pages</span>
                    <span style={{ fontSize: '14px', fontWeight: 600 }}>{course.page_count}</span>
                  </div>
                </div>
                <div className="text-xs text-muted">
                  {formatDate(course.last_synced_at)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
