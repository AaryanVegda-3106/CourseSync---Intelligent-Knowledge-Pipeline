/* ──────────────────────────────────────────────────────────
   CourseSync — TypeScript Type Definitions
   Mirrors backend Pydantic schemas exactly.
   ────────────────────────────────────────────────────────── */

// ── Content Type Enum (PRD §9.2) ──────────────────────────

export type ContentType =
  | 'course_overview'
  | 'module'
  | 'lecture'
  | 'reading'
  | 'quiz'
  | 'assignment'
  | 'project'
  | 'announcement'
  | 'reference'
  | 'pdf'
  | 'video'
  | 'other';

export type CourseStatus =
  | 'created'
  | 'discovering'
  | 'discovered'
  | 'ingesting'
  | 'ingested'
  | 'processing'
  | 'processed'
  | 'exporting'
  | 'exported'
  | 'failed';

export type JobStage =
  | 'mapping'
  | 'discovering'
  | 'scraping'
  | 'processing'
  | 'exporting'
  | 'complete'
  | 'failed';

export type PageStatus =
  | 'discovered'
  | 'selected'
  | 'scraping'
  | 'scraped'
  | 'processing'
  | 'processed'
  | 'failed'
  | 'skipped';

// ── Models ────────────────────────────────────────────────

export interface Course {
  id: string;
  name: string;
  url: string;
  status: CourseStatus;
  module_count: number;
  page_count: number;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CourseListResponse {
  courses: Course[];
  total: number;
}

export interface PageInfo {
  id: string;
  title: string | null;
  url: string;
  content_type: ContentType;
  status: PageStatus;
}

export interface ModuleInfo {
  id: string;
  title: string;
  order_index: number;
  pages: PageInfo[];
}

export interface CourseHierarchy {
  course: string;
  course_id: string;
  modules: ModuleInfo[];
  unclassified_pages: PageInfo[];
}

export interface IngestionJob {
  job_id: string;
  course_id: string;
  current_stage: JobStage;
  pages_discovered: number;
  pages_scraped: number;
  pages_failed: number;
  pages_processed: number;
  files_generated: number;
  started_at: string;
  completed_at: string | null;
  error: string | null;
}

export interface ExportFile {
  filename: string;
  file_type: string;
  size_bytes: number;
  created_at: string;
}

export interface ExportListResponse {
  course_id: string;
  files: ExportFile[];
}

// ── Request Bodies ────────────────────────────────────────

export interface CourseCreateRequest {
  name: string;
  url: string;
}

export interface IngestRequest {
  page_ids: string[];
}
