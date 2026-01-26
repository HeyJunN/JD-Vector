/**
 * 역량 레이블 매핑 유틸리티
 * 영문 키워드를 한글 레이블로 변환
 */

// 영문 역량 키워드를 한글로 매핑
export const COMPETENCY_LABEL_MAP: Record<string, string> = {
  // 주요 역량 카테고리
  requirements: '필수 역량',
  required: '필수 역량',
  preferred: '우대 사항',
  preference: '우대 사항',
  preferences: '우대 사항',
  experience: '경력/경험',
  experiences: '경력/경험',
  potential: '성장 잠재력',
  technical: '기술 스택',

  // 세부 카테고리
  skills: '기술 역량',
  skill: '기술 역량',
  education: '학력/교육',
  certifications: '자격증',
  certification: '자격증',
  languages: '언어 능력',
  language: '언어 능력',
  projects: '프로젝트 경험',
  project: '프로젝트 경험',
  responsibilities: '업무 책임',
  responsibility: '업무 책임',
  qualifications: '자격 요건',
  qualification: '자격 요건',
  soft_skills: '소프트 스킬',
  hard_skills: '하드 스킬',
  tools: '도구/툴',
  tool: '도구/툴',
  frameworks: '프레임워크',
  framework: '프레임워크',
  methodologies: '방법론',
  methodology: '방법론',
  domain_knowledge: '도메인 지식',

  // 기타 일반 용어
  overview: '전체 개요',
  summary: '요약',
  background: '배경',
  achievements: '성과',
  achievement: '성과',
  leadership: '리더십',
  collaboration: '협업 능력',
  communication: '커뮤니케이션',
  problem_solving: '문제 해결',
  creativity: '창의성',
  adaptability: '적응력',
  time_management: '시간 관리',
  decision_making: '의사결정',
  critical_thinking: '비판적 사고',
  teamwork: '팀워크',
  motivation: '동기부여',
  initiative: '주도성',
  analytical: '분석 능력',
  organizational: '조직 능력',

  // 기술 관련
  programming: '프로그래밍',
  coding: '코딩',
  development: '개발',
  design: '디자인',
  architecture: '아키텍처',
  testing: '테스팅',
  debugging: '디버깅',
  deployment: '배포',
  maintenance: '유지보수',
  documentation: '문서화',

  // 업무 관련
  management: '관리',
  planning: '기획',
  analysis: '분석',
  research: '리서치',
  strategy: '전략',
  operations: '운영',
  marketing: '마케팅',
  sales: '영업',
  customer_service: '고객 서비스',
};

/**
 * 영문 키를 한글 레이블로 변환
 * 매핑되지 않은 경우 첫 글자를 대문자로 변환하여 반환
 *
 * @param englishKey - 변환할 영문 키
 * @returns 한글 레이블 또는 포맷팅된 영문
 *
 * @example
 * getKoreanLabel('requirements') // '필수 역량'
 * getKoreanLabel('technical_skills') // 'Technical skills'
 * getKoreanLabel('NEW_CATEGORY') // 'New category'
 */
export const getKoreanLabel = (englishKey: string): string => {
  if (!englishKey) return '';

  // 소문자로 변환하여 매핑 확인
  const normalizedKey = englishKey.toLowerCase().trim();

  // 매핑된 한글이 있으면 반환
  if (COMPETENCY_LABEL_MAP[normalizedKey]) {
    return COMPETENCY_LABEL_MAP[normalizedKey];
  }

  // 언더스코어와 하이픈을 공백으로 치환
  const formatted = normalizedKey.replace(/[_-]/g, ' ');

  // 각 단어의 첫 글자를 대문자로 변환 (fallback)
  return formatted
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * 여러 키를 한 번에 변환
 *
 * @param keys - 변환할 영문 키 배열
 * @returns 한글 레이블 배열
 */
export const getKoreanLabels = (keys: string[]): string[] => {
  return keys.map(getKoreanLabel);
};

/**
 * 객체의 특정 필드를 한글로 변환
 *
 * @param obj - 변환할 객체
 * @param field - 변환할 필드명
 * @returns 변환된 객체
 */
export const transformObjectLabel = <T extends Record<string, any>>(
  obj: T,
  field: keyof T
): T => {
  if (!obj[field] || typeof obj[field] !== 'string') {
    return obj;
  }

  return {
    ...obj,
    [field]: getKoreanLabel(obj[field] as string),
  };
};
