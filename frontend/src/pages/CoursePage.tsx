import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Course, CourseHierarchy, IngestionJob, ExportFile, ModuleInfo } from '../types';
import {
  getCourse,
  getCourseStructure,
  ingestCourse,
  getProgress,
  processCourse,
  exportCourse,
  listFiles,
  getFileDownloadUrl,
  getZipDownloadUrl,
} from '../services/api';

const CONTENT_TYPE_ICONS: Record<string, string> = {
  lecture: '📖',
  reading: '📄',
  quiz: '❓',
  assignment: '📝',
  project: '🔬',
  module: '📦',
  course_overview: '🏠',
  announcement: '📢',
  reference: '📚',
  pdf: '📎',
  video: '🎥',
  other: '📄',
};

export default function CoursePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [course, setCourse] = useState<Course | null>(null);
  const [hierarchy, setHierarchy] = useState<CourseHierarchy | null>(null);
  const [selectedPages, setSelectedPages] = useState<Set<string>>(new Set());
  const [job, setJob] = useState<IngestionJob | null>(null);
  const [files, setFiles] = useState<ExportFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'structure' | 'progress' | 'exports'>('structure');

  useEffect(() => {
    if (id) loadCourse(id);
  }, [id]);

  async function loadCourse(courseId: string) {
    try {
      setLoading(true);
      const c = await getCourse(courseId);
      setCourse(c);

      // Load hierarchy if discovered
      if (['discovered', 'ingesting', 'ingested', 'processing', 'processed', 'exporting', 'exported'].includes(c.status)) {
        const h = await getCourseStructure(courseId);
        setHierarchy(h);

        // Pre-select all pages
        const pageIds = new Set<string>();
        h.modules.forEach(m => m.pages.forEach(p => pageIds.add(p.id)));
        h.unclassified_pages.forEach(p => pageIds.add(p.id));
        setSelectedPages(pageIds);
      }

      // Load progress if ingesting/processing
      if (['ingesting', 'processing', 'exporting'].includes(c.status)) {
        try {
          const j = await getProgress(courseId);
          setJob(j);
          setTab('progress');
        } catch { /* no job yet */ }
      }

      // Load files if exported
      if (['exported', 'processed'].includes(c.status)) {
        try {
          const f = await listFiles(courseId);
          setFiles(f.files);
          if (f.files.length > 0) setTab('exports');
        } catch { /* no files yet */ }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load course');
    } finally {
      setLoading(false);
    }
  }

  // ── Page selection ───────────────────────────────────

  function togglePage(pageId: string) {
    setSelectedPages(prev => {
      const next = new Set(prev);
      next.has(pageId) ? next.delete(pageId) : next.add(pageId);
      return next;
    });
  }

  function toggleModule(module: ModuleInfo) {
    const modulePageIds = module.pages.map(p => p.id);
    const allSelected = modulePageIds.every(id => selectedPages.has(id));
    setSelectedPages(prev => {
      const next = new Set(prev);
      modulePageIds.forEach(id => allSelected ? next.delete(id) : next.add(id));
      return next;
    });
  }

  function selectAll() {
    if (!hierarchy) return;
    const all = new Set<string>();
    hierarchy.modules.forEach(m => m.pages.forEach(p => all.add(p.id)));
    hierarchy.unclassified_pages.forEach(p => all.add(p.id));
    setSelectedPages(all);
  }

  function selectNone() {
    setSelectedPages(new Set());
  }

  // ── Actions ──────────────────────────────────────────

  async function handleIngest() {
    if (!id || selectedPages.size === 0) return;
    setActionLoading('ingest');
    setError(null);
    try {
      const j = await ingestCourse(id, { page_ids: Array.from(selectedPages) });
      setJob(j);
      setTab('progress');
      // Start polling
      pollProgress(id);
    } catch (err: any) {
      setError(err.detail || 'Ingestion failed');
    } finally {
      setActionLoading(null);
    }
  }

  async function handleProcess() {
    if (!id) return;
    setActionLoading('process');
    setError(null);
    try {
      await processCourse(id);
      // Poll for updates
      pollProgress(id);
    } catch (err: any) {
      setError(err.detail || 'Processing failed');
    } finally {
      setActionLoading(null);
    }
  }

  async function handleExport() {
    if (!id) return;
    setActionLoading('export');
    setError(null);
    try {
      await exportCourse(id);
      // Reload files
      const f = await listFiles(id);
      setFiles(f.files);
      setTab('exports');
      // Reload course status
      const c = await getCourse(id);
      setCourse(c);
    } catch (err: any) {
      setError(err.detail || 'Export failed');
    } finally {
      setActionLoading(null);
    }
  }

  // ── Polling ──────────────────────────────────────────

  const pollProgress = useCallback(async (courseId: string) => {
    const poll = async () => {
      try {
        let j = null;
        try {
          j = await getProgress(courseId);
          setJob(j);
        } catch { /* ignore */ }
        
        const c = await getCourse(courseId);
        setCourse(c);

        const isJobActive = j ? !['complete', 'failed'].includes(j.current_stage) : false;
        const isCourseActive = ['discovering', 'ingesting', 'processing', 'exporting'].includes(c.status);

        if (isJobActive || isCourseActive) {
          setTimeout(poll, 2000);
        } else {
          // Reload files after completion
          try {
            const f = await listFiles(courseId);
            setFiles(f.files);
          } catch { /* ignore */ }
        }
      } catch {
        // Stop polling on error
      }
    };
    poll();
  }, []);

  // ── Render ───────────────────────────────────────────

  if (loading) {
    return (
      <div className="page-container flex items-center" style={{ justifyContent: 'center', padding: '80px 0' }}>
        <div className="spinner spinner-lg" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="page-container">
        <div className="empty-state">
          <div className="empty-state-title">Course not found</div>
          <button className="btn btn-primary mt-4" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
        </div>
      </div>
    );
  }

  const STATUS_BADGE: Record<string, string> = {
    created: 'badge-neutral', discovering: 'badge-info', discovered: 'badge-accent',
    ingesting: 'badge-info', ingested: 'badge-success', processing: 'badge-warning',
    processed: 'badge-success', exporting: 'badge-warning', exported: 'badge-success',
    failed: 'badge-error',
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center gap-3">
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/dashboard')}>← Back</button>
          <span className={`badge ${STATUS_BADGE[course.status] || 'badge-neutral'}`}>{course.status}</span>
        </div>
        <h1 className="page-title mt-2">{course.name}</h1>
        <p className="page-subtitle truncate">{course.url}</p>
      </div>

      {/* Stats */}
      <div className="stat-grid mb-4">
        <div className="stat-card">
          <div className="stat-value">{course.module_count}</div>
          <div className="stat-label">Modules</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{course.page_count}</div>
          <div className="stat-label">Pages</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{selectedPages.size}</div>
          <div className="stat-label">Selected</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{files.length}</div>
          <div className="stat-label">Exports</div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div
          style={{
            background: 'var(--color-error-muted)',
            color: 'var(--color-error)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            fontSize: '13px',
            marginBottom: 16,
          }}
        >
          {error}
          <button className="btn btn-ghost btn-sm" onClick={() => setError(null)} style={{ marginLeft: 8 }}>✕</button>
        </div>
      )}

      {/* Action Bar */}
      <div className="flex gap-3 mb-4" style={{ flexWrap: 'wrap' }}>
        <button
          className="btn btn-primary"
          onClick={handleIngest}
          disabled={selectedPages.size === 0 || actionLoading === 'ingest'}
          id="btn-ingest"
        >
          {actionLoading === 'ingest' && <div className="spinner" />}
          Scrape Selected ({selectedPages.size})
        </button>
        <button
          className="btn btn-secondary"
          onClick={handleProcess}
          disabled={!['ingested', 'processed', 'exported', 'failed'].includes(course.status) || actionLoading === 'process'}
          id="btn-process"
        >
          {actionLoading === 'process' && <div className="spinner" />}
          AI Structure
        </button>
        <button
          className="btn btn-secondary"
          onClick={handleExport}
          disabled={!['processed', 'exported'].includes(course.status) || actionLoading === 'export'}
          id="btn-export"
        >
          {actionLoading === 'export' && <div className="spinner" />}
          Generate Exports
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {(['structure', 'progress', 'exports'] as const).map(t => (
          <button
            key={t}
            className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setTab(t)}
          >
            {t === 'structure' ? 'Structure' : t === 'progress' ? 'Progress' : 'Exports'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'structure' && hierarchy && (
        <div className="card">
          <div className="card-header">
            <span className="card-title">Course Hierarchy</span>
            <div className="flex gap-2">
              <button className="btn btn-ghost btn-sm" onClick={selectAll}>Select All</button>
              <button className="btn btn-ghost btn-sm" onClick={selectNone}>Clear</button>
            </div>
          </div>

          {hierarchy.modules.map(module => {
            const moduleAllSelected = module.pages.every(p => selectedPages.has(p.id));
            const moduleSomeSelected = module.pages.some(p => selectedPages.has(p.id));

            return (
              <div key={module.id} className="tree-module">
                <div className="tree-module-header" onClick={() => toggleModule(module)}>
                  <input
                    type="checkbox"
                    className="checkbox"
                    checked={moduleAllSelected}
                    ref={el => { if (el) el.indeterminate = moduleSomeSelected && !moduleAllSelected; }}
                    onChange={() => toggleModule(module)}
                  />
                  <span style={{ fontSize: '14px' }}>📦</span>
                  <span className="tree-module-title">{module.title}</span>
                  <span className="badge badge-neutral">{module.pages.length} pages</span>
                </div>
                {module.pages.map(page => (
                  <div key={page.id} className="tree-page">
                    <input
                      type="checkbox"
                      className="checkbox"
                      checked={selectedPages.has(page.id)}
                      onChange={() => togglePage(page.id)}
                    />
                    <span>{CONTENT_TYPE_ICONS[page.content_type] || '📄'}</span>
                    <span className="tree-page-title">{page.title || page.url}</span>
                    <span className="badge badge-neutral">{page.content_type}</span>
                  </div>
                ))}
              </div>
            );
          })}

          {hierarchy.unclassified_pages.length > 0 && (
            <div className="tree-module">
              <div className="tree-module-header">
                <span className="tree-module-title text-muted">Unclassified Pages</span>
                <span className="badge badge-neutral">{hierarchy.unclassified_pages.length}</span>
              </div>
              {hierarchy.unclassified_pages.map(page => (
                <div key={page.id} className="tree-page">
                  <input
                    type="checkbox"
                    className="checkbox"
                    checked={selectedPages.has(page.id)}
                    onChange={() => togglePage(page.id)}
                  />
                  <span>{CONTENT_TYPE_ICONS[page.content_type] || '📄'}</span>
                  <span className="tree-page-title">{page.title || page.url}</span>
                  <span className="badge badge-neutral">{page.content_type}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'progress' && (
        <div className="card">
          <div className="card-title mb-4">Ingestion Progress</div>

          {job ? (
            <div className="flex flex-col gap-4">
              {/* Stage Indicator */}
              <div className="stage-indicator">
                {['mapping', 'scraping', 'processing', 'exporting', 'complete'].map((stage) => {
                  const stageOrder = ['mapping', 'discovering', 'scraping', 'processing', 'exporting', 'complete'];
                  const currentIdx = stageOrder.indexOf(job.current_stage);
                  const stageIdx = stageOrder.indexOf(stage);
                  const isComplete = stageIdx < currentIdx;
                  const isActive = stage === job.current_stage;

                  return (
                    <div key={stage} className={`stage-step ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''}`}>
                      <div className="stage-step-dot" />
                      {stage}
                    </div>
                  );
                })}
              </div>

              {/* Progress Bar */}
              {job.pages_discovered > 0 && (
                <div>
                  <div className="flex justify-between mb-2 text-xs">
                    <span className="text-secondary">
                      {job.pages_scraped} / {job.pages_discovered} pages scraped
                    </span>
                    <span className="text-muted">
                      {job.pages_failed > 0 && `${job.pages_failed} failed`}
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${(job.pages_scraped / job.pages_discovered) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Stats */}
              <div className="stat-grid">
                <div className="stat-card">
                  <div className="stat-value">{job.pages_discovered}</div>
                  <div className="stat-label">Discovered</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{job.pages_scraped}</div>
                  <div className="stat-label">Scraped</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{job.pages_processed}</div>
                  <div className="stat-label">Processed</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{job.files_generated}</div>
                  <div className="stat-label">Files</div>
                </div>
              </div>

              {/* Error */}
              {job.error && (
                <div style={{
                  background: 'var(--color-warning-muted)',
                  color: 'var(--color-warning)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '13px',
                }}>
                  {job.error}
                </div>
              )}

              {/* Completed */}
              {job.current_stage === 'complete' && (
                <div style={{
                  background: 'var(--color-success-muted)',
                  color: 'var(--color-success)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '13px',
                  fontWeight: 500,
                }}>
                  ✓ Ingestion complete
                </div>
              )}
            </div>
          ) : (
            <div className="text-sm text-muted">No ingestion job started yet. Select pages and click "Scrape Selected" to begin.</div>
          )}
        </div>
      )}

      {tab === 'exports' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="card-title">Export Files</div>
            {files.length > 0 && (
              <a
                href={getZipDownloadUrl(id!)}
                className="btn btn-primary btn-sm"
              >
                Download All (ZIP)
              </a>
            )}
          </div>

          {files.length === 0 ? (
            <div className="text-sm text-muted">
              No export files yet. Process content with AI first, then generate exports.
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {files.map(file => (
                <div key={file.filename} className="file-item">
                  <div className="file-icon">
                    {file.file_type === 'source' ? '📄' : file.file_type === 'knowledge' ? '🧠' : file.file_type === 'quiz' ? '❓' : file.file_type === 'glossary' ? '📖' : '📁'}
                  </div>
                  <div className="file-info">
                    <div className="file-name">{file.filename}</div>
                    <div className="file-meta">
                      {file.file_type} · {(file.size_bytes / 1024).toFixed(1)} KB
                    </div>
                  </div>
                  <a
                    href={getFileDownloadUrl(id!, file.filename)}
                    download={file.filename}
                    className="btn btn-secondary btn-sm"
                  >
                    Download
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
