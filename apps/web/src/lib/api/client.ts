/**
 * API Client Configuration
 * axios 인스턴스 설정 및 기본 에러 핸들링
 */

import axios, { AxiosError, AxiosInstance } from 'axios';
import type { UploadErrorResponse } from './types';

// 환경 변수에서 API URL 가져오기 (없으면 기본값 사용)
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Axios 인스턴스 생성
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60초 (대용량 PDF 처리 고려)
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 요청 인터셉터: 요청 로깅 (개발 환경)
 */
apiClient.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/**
 * 응답 인터셉터: 에러 처리 및 로깅
 */
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.url}`, response.data);
    }
    return response;
  },
  (error: AxiosError<UploadErrorResponse>) => {
    // 에러 로깅
    if (import.meta.env.DEV) {
      console.error('[API Error]', {
        url: error.config?.url,
        status: error.response?.status,
        data: error.response?.data,
      });
    }

    // 에러 메시지 추출 및 표준화
    const errorMessage = extractErrorMessage(error);

    // 커스텀 에러 객체 생성
    const customError = new Error(errorMessage);
    (customError as any).originalError = error;
    (customError as any).statusCode = error.response?.status;
    (customError as any).errorCode = error.response?.data?.error?.code;

    return Promise.reject(customError);
  }
);

/**
 * 에러 메시지 추출 함수
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function extractErrorMessage(error: AxiosError<any>): string {
  // 네트워크 에러 (백엔드 서버가 다운되었거나, CORS 에러)
  if (error.code === 'ERR_NETWORK' || !error.response) {
    return '서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.';
  }

  const data = error.response?.data;

  // FastAPI 에러 형식: { detail: { error: { code, message } } }
  const detail = data?.detail;
  if (detail?.error?.message) {
    const { message, code } = detail.error;
    switch (code) {
      case 'FILE_TOO_LARGE':
        return '파일 크기가 너무 큽니다. 20MB 이하의 파일을 업로드해주세요.';
      case 'INVALID_FILE_TYPE':
        return '지원하지 않는 파일 형식입니다. PDF 파일만 업로드 가능합니다.';
      case 'PDF_PARSE_ERROR':
        return 'PDF 파일을 읽는 중 오류가 발생했습니다. 파일이 손상되었거나 암호화되어 있을 수 있습니다.';
      case 'DOCUMENT_NOT_FOUND':
        return message || '문서를 찾을 수 없습니다. 파일을 다시 업로드해주세요.';
      case 'RESUME_NOT_FOUND':
      case 'JD_NOT_FOUND':
        return message || '문서를 찾을 수 없습니다.';
      case 'RESUME_NOT_VECTORIZED':
      case 'JD_NOT_VECTORIZED':
        return message || '문서 임베딩이 완료되지 않았습니다.';
      default:
        return message || '오류가 발생했습니다.';
    }
  }

  // 기존 에러 형식: { error: { code, message } }
  if (data?.error) {
    const { message, code } = data.error;
    switch (code) {
      case 'FILE_TOO_LARGE':
        return '파일 크기가 너무 큽니다. 20MB 이하의 파일을 업로드해주세요.';
      case 'INVALID_FILE_TYPE':
        return '지원하지 않는 파일 형식입니다. PDF 파일만 업로드 가능합니다.';
      case 'PDF_PARSE_ERROR':
        return 'PDF 파일을 읽는 중 오류가 발생했습니다. 파일이 손상되었거나 암호화되어 있을 수 있습니다.';
      case 'VALIDATION_ERROR':
        return message || '입력 데이터가 올바르지 않습니다.';
      default:
        return message || '파일 업로드 중 오류가 발생했습니다.';
    }
  }

  // HTTP 상태 코드 기반 기본 메시지
  const status = error.response?.status;
  switch (status) {
    case 400:
      return '잘못된 요청입니다.';
    case 404:
      return '요청한 리소스를 찾을 수 없습니다.';
    case 413:
      return '파일 크기가 너무 큽니다.';
    case 415:
      return '지원하지 않는 파일 형식입니다.';
    case 422:
      return 'PDF 파일을 처리할 수 없습니다.';
    case 500:
      return '서버 내부 오류가 발생했습니다.';
    case 503:
      return '서비스를 일시적으로 사용할 수 없습니다.';
    default:
      return error.message || '알 수 없는 오류가 발생했습니다.';
  }
}

/**
 * API 클라이언트 설정 정보 조회
 */
export const getApiConfig = () => ({
  baseURL: API_BASE_URL,
  timeout: apiClient.defaults.timeout,
  environment: import.meta.env.MODE,
});

/**
 * 개발 환경에서 API 설정 정보 출력
 */
if (import.meta.env.DEV) {
  console.log('[API Client] Configuration:', getApiConfig());
}
