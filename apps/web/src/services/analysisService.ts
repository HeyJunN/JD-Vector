/**
 * Analysis Service - 분석 API 호출
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface MatchRequest {
  resume_id: string;
  jd_id: string;
}

export interface MatchResponse {
  success: boolean;
  data: {
    resume_file_id: string;
    jd_file_id: string;
    overall_similarity: number;
    match_score: number;
    match_grade: 'S' | 'A' | 'B' | 'C' | 'D';
    section_scores: Array<{
      section_type: string;
      score: number;
      chunk_count: number;
      top_matches: any[];
    }>;
    chunk_match_count: number;
    similar_tech_matches: Array<{
      jd_required: string;
      resume_has: string;
      relationship: string;
    }>;
    similar_tech_bonus: number;
    feedback: {
      summary: string;
      strengths: any[];
      improvements: any[];
      potential: any[];
      action_items: string[];
    };
  } | null;
  message: string;
}

export interface GapAnalysisResponse {
  success: boolean;
  data: {
    match_result: any;
    strengths: any[];
    weaknesses: any[];
    feedback: any;
    similar_technologies: any[];
  } | null;
  message: string;
}

export interface DocumentStatusResponse {
  document_id: string | null;
  file_id: string;
  filename: string | null;
  file_type: string | null;
  embedding_status: string | null;
  chunk_count: number;
  created_at: string | null;
}

export const analysisService = {
  /**
   * 문서 상태 조회 (file_id로 document_id 얻기)
   */
  async getDocumentStatus(fileId: string): Promise<DocumentStatusResponse> {
    try {
      const response = await axios.get<DocumentStatusResponse>(
        `${API_BASE_URL}/api/v1/analysis/documents/${fileId}`
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || '문서 상태 조회에 실패했습니다.'
        );
      }
      throw error;
    }
  },

  /**
   * 이력서-JD 매칭 분석
   */
  async analyzeMatch(request: MatchRequest): Promise<MatchResponse> {
    try {
      const response = await axios.post<MatchResponse>(
        `${API_BASE_URL}/api/v1/analysis/match`,
        request,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || '분석에 실패했습니다.'
        );
      }
      throw error;
    }
  },

  /**
   * 스킬 갭 분석
   */
  async analyzeGap(request: MatchRequest): Promise<GapAnalysisResponse> {
    try {
      const response = await axios.post<GapAnalysisResponse>(
        `${API_BASE_URL}/api/v1/analysis/gap-analysis`,
        request,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || '갭 분석에 실패했습니다.'
        );
      }
      throw error;
    }
  },

  /**
   * 분석 서비스 헬스 체크
   */
  async checkHealth(): Promise<{ status: string; service: string }> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/analysis/health`);
      return response.data;
    } catch (error) {
      throw new Error('분석 서비스에 연결할 수 없습니다.');
    }
  },
};

export default analysisService;
