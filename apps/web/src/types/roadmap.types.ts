/**
 * Roadmap Types - 백엔드 API 응답과 일치하는 타입 정의
 */

export interface LearningResource {
  title: string;
  url: string;
  type: 'documentation' | 'tutorial' | 'video' | 'article' | 'course';
  platform: 'YouTube' | 'Inflearn' | 'Nomad' | 'Official' | 'MDN' | 'Docs' | 'GitHub';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  description?: string;
  estimated_hours?: number;
}

export interface RoadmapTask {
  task: string;
  completed: boolean;
  priority?: 'high' | 'medium' | 'low';
}

export interface RoadmapWeek {
  week_number: number;
  title: string;
  duration: string;
  description: string;
  keywords: string[];
  tasks: RoadmapTask[];
  resources: LearningResource[];
}

export interface RoadmapData {
  total_weeks: number;
  match_grade: 'S' | 'A' | 'B' | 'C' | 'D';
  target_grade: string;
  summary: string;
  weekly_plan: RoadmapWeek[];
  key_improvement_areas: string[];
}

export interface RoadmapResponse {
  success: boolean;
  data: RoadmapData | null;
  message: string;
}

export interface RoadmapGenerateRequest {
  resume_id: string;
  jd_id: string;
  target_weeks?: number;
}

// 로컬 상태 관리용 타입 (completed 상태 추적)
export interface RoadmapState extends RoadmapData {
  completedTasks: Set<string>; // "week_number-task_index" 형태로 저장
}

// 진행률 계산용 타입
export interface ProgressStats {
  totalTasks: number;
  completedTasks: number;
  percentage: number;
}

export interface WeekProgressStats extends ProgressStats {
  week_number: number;
}
