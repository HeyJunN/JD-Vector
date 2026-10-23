/**
 * Upload API Functions
 * 파일 업로드 관련 API 호출 함수
 */

import { apiClient } from './client';
import type {
  UploadParams,
  UploadResponse,
  UploadResponseData,
  UploadProgress,
} from './types';

/**
 * PDF 파일 업로드 API
 *
 * @param params - 업로드 파라미터 (file, file_type, extract_tables, parser_type)
 * @param onProgress - 진행 상태 콜백 함수 (optional)
 * @returns UploadResponseData
 * @throws Error - 업로드 실패 시
 */
export async function uploadPDF(
  params: UploadParams,
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadResponseData> {
  const { file, file_type, extract_tables = false, parser_type = 'auto' } = params;

  // FormData 생성
  const formData = new FormData();
  formData.append('file', file);
  formData.append('file_type', file_type);
  formData.append('extract_tables', String(extract_tables));
  formData.append('parser_type', parser_type);
  formData.append('auto_vectorize', 'true');  // 자동 벡터화 활성화

  try {
    // API 요청
    const response = await apiClient.post<UploadResponse>(
      '/api/v1/upload/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // 업로드 진행 상태 추적
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentage = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress({
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage,
            });
          }
        },
      }
    );

    // 성공 응답 데이터 반환
    if (response.data.success && response.data.data) {
      return response.data.data;
    }

    // 예상치 못한 응답 형식
    throw new Error('업로드 응답 형식이 올바르지 않습니다.');
  } catch (error) {
    // axios 인터셉터에서 이미 에러 처리가 되어 있으므로, 그대로 전파
    throw error;
  }
}

/**
 * 이력서 파일 업로드 (편의 함수)
 *
 * @param file - 이력서 PDF 파일
 * @param onProgress - 진행 상태 콜백 함수 (optional)
 * @returns UploadResponseData
 */
export async function uploadResume(
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadResponseData> {
  return uploadPDF(
    {
      file,
      file_type: 'resume',
      parser_type: 'pypdf', // 이력서는 PyPDF 권장
    },
    onProgress
  );
}

/**
 * 채용 공고 파일 업로드 (편의 함수)
 *
 * @param file - 채용 공고 PDF 파일
 * @param onProgress - 진행 상태 콜백 함수 (optional)
 * @returns UploadResponseData
 */
export async function uploadJobDescription(
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadResponseData> {
  return uploadPDF(
    {
      file,
      file_type: 'job_description',
      extract_tables: true, // JD는 테이블 추출 권장
      parser_type: 'pdfplumber',
    },
    onProgress
  );
}

/**
 * 업로드 헬스 체크
 *
 * @returns 서비스 상태
 */
export async function checkUploadHealth(): Promise<{
  status: string;
  service: string;
  message: string;
}> {
  const response = await apiClient.get('/api/v1/upload/health');
  return response.data;
}
