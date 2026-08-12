/* ──────────────────────────────────────────────────────────
   CourseSync — API Client Service
   Typed HTTP client for all backend endpoints.
   ────────────────────────────────────────────────────────── */

import type {
  Course,
  CourseListResponse,
  CourseCreateRequest,
  CourseHierarchy,
  IngestionJob,
  IngestRequest,
  ExportListResponse,
} from '../types';

const BASE_URL = '/api';

class ApiError extends Error {
  status: number;
  detail: string | null;

  constructor(status: number, message: string, detail: string | null = null) {
    super(message);
    this.status = status;
    this.detail = detail;
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let detail = null;
    try {
      const errorBody = await res.json();
      detail = errorBody.detail || errorBody.error || null;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(res.status, `Request failed: ${res.statusText}`, detail);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json() as Promise<T>;
}

// ── Courses ──────────────────────────────────────────────

export async function createCourse(data: CourseCreateRequest): Promise<Course> {
  return request<Course>('/courses', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function listCourses(): Promise<CourseListResponse> {
  return request<CourseListResponse>('/courses');
}

export async function getCourse(id: string): Promise<Course> {
  return request<Course>(`/courses/${id}`);
}

export async function deleteCourse(id: string): Promise<void> {
  return request<void>(`/courses/${id}`, {
    method: 'DELETE',
  });
}

// ── Discovery ────────────────────────────────────────────

export async function discoverCourse(id: string): Promise<CourseHierarchy> {
  return request<CourseHierarchy>(`/courses/${id}/discover`, {
    method: 'POST',
  });
}

export async function getCourseStructure(id: string): Promise<CourseHierarchy> {
  return request<CourseHierarchy>(`/courses/${id}/structure`);
}

// ── Ingestion ────────────────────────────────────────────

export async function ingestCourse(id: string, data: IngestRequest): Promise<IngestionJob> {
  return request<IngestionJob>(`/courses/${id}/ingest`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getProgress(id: string): Promise<IngestionJob> {
  return request<IngestionJob>(`/courses/${id}/progress`);
}

// ── Processing ───────────────────────────────────────────

export async function processCourse(id: string): Promise<{ message: string }> {
  return request<{ message: string }>(`/courses/${id}/process`, {
    method: 'POST',
  });
}

// ── Export ────────────────────────────────────────────────

export async function exportCourse(id: string): Promise<{ files_generated: number; filenames: string[] }> {
  return request<{ files_generated: number; filenames: string[] }>(`/courses/${id}/export`, {
    method: 'POST',
  });
}

export async function listFiles(id: string): Promise<ExportListResponse> {
  return request<ExportListResponse>(`/courses/${id}/files`);
}

export function getFileDownloadUrl(courseId: string, filename: string): string {
  return `${BASE_URL}/courses/${courseId}/files/${filename}`;
}

export function getZipDownloadUrl(courseId: string): string {
  return `${BASE_URL}/courses/${courseId}/download-zip`;
}
