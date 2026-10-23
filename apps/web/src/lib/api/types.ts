/**
 * API Response Types
 * 백엔드 API 응답 스키마와 일치하는 TypeScript 타입 정의
 */

// ============================================================================
// Upload API Types
// ============================================================================

export type FileType = 'resume' | 'job_description';
export type ParserType = 'auto' | 'pypdf' | 'pdfplumber' | 'pymupdf';

/**
 * PDF 메타데이터
 */
export interface PDFMetadata {
  author?: string;
  created_date?: string;
  modified_date?: string;
  title?: string;
  subject?: string;
  page_count: number;
  has_tables: boolean;
  language: string;
  parser_used: string;
  file_size_bytes: number;
  extraction_time_ms: number;
}

/**
 * 업로드 응답 데이터
 */
export interface UploadResponseData {
  file_id: string;
  filename: string;
  file_type: FileType;
  text_content: string;
  cleaned_text: string;
  word_count: number;
  char_count: number;
  metadata: PDFMetadata;
}

/**
 * 업로드 API 성공 응답
 */
export interface UploadResponse {
  success: true;
  data: UploadResponseData;
  message: string;
}

/**
 * 에러 상세 정보
 */
export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * 업로드 API 에러 응답
 */
export interface UploadErrorResponse {
  success: false;
  error: ErrorDetail;
}

/**
 * 업로드 요청 파라미터
 */
export interface UploadParams {
  file: File;
  file_type: FileType;
  extract_tables?: boolean;
  parser_type?: ParserType;
}

/**
 * 업로드 진행 상태
 */
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

// ============================================================================
// Analysis API Types (Phase 3에서 구현 예정)
// ============================================================================

export interface AnalysisRequest {
  resume_file_id: string;
  jd_file_id: string;
}

export interface AnalysisResponse {
  success: boolean;
  data?: any;
  message?: string;
  error?: ErrorDetail;
}

// ============================================================================
// Roadmap API Types (Phase 5에서 구현 예정)
// ============================================================================

export interface RoadmapRequest {
  analysis_id: string;
}

export interface RoadmapResponse {
  success: boolean;
  data?: any;
  message?: string;
  error?: ErrorDetail;
}
