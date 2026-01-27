/**
 * Roadmap Service - 로드맵 API 호출
 */

import axios from 'axios';
import type { RoadmapGenerateRequest, RoadmapResponse } from '../types/roadmap.types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const roadmapService = {
  /**
   * 로드맵 생성 요청
   */
  async generateRoadmap(request: RoadmapGenerateRequest): Promise<RoadmapResponse> {
    try {
      const response = await axios.post<RoadmapResponse>(
        `${API_BASE_URL}/api/v1/roadmap/generate`,
        request,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 120000, // 120초 (2분) 타임아웃 설정 - 로드맵 생성은 시간이 오래 걸림
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          error.response?.data?.message || '로드맵 생성에 실패했습니다.'
        );
      }
      throw error;
    }
  },

  /**
   * 로드맵 서비스 헬스 체크
   */
  async checkHealth(): Promise<{ status: string; service: string }> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/roadmap/health`);
      return response.data;
    } catch (error) {
      throw new Error('로드맵 서비스에 연결할 수 없습니다.');
    }
  },
};

export default roadmapService;
