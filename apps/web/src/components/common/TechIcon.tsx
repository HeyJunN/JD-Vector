/**
 * TechIcon Component - 기술 키워드를 아이콘으로 자동 매핑
 *
 * 백엔드에서 전달하는 표준화된 keywords(소문자)를 lucide-react 아이콘으로 변환
 */

import {
  Code2,
  FileCode,
  Database,
  Server,
  Globe,
  GitBranch,
  Container,
  Cloud,
  TestTube,
  Package,
  Boxes,
  Rocket,
  Briefcase,
  FileText,
  Users,
  Layout,
  Palette,
  Workflow,
  Settings,
  BookOpen,
  Video,
  GraduationCap,
  type LucideIcon,
} from 'lucide-react';

interface TechIconProps {
  keyword: string;
  className?: string;
  size?: number;
}

// 기술 키워드 -> 아이콘 매핑
const TECH_ICON_MAP: Record<string, LucideIcon> = {
  // 프론트엔드
  react: Code2,
  vue: Code2,
  angular: Code2,
  svelte: Code2,
  nextjs: FileCode,
  'next.js': FileCode,
  typescript: FileCode,
  javascript: FileCode,
  js: FileCode,
  ts: FileCode,
  html: Layout,
  css: Palette,
  tailwind: Palette,
  tailwindcss: Palette,

  // 상태관리
  redux: Workflow,
  zustand: Workflow,
  recoil: Workflow,
  mobx: Workflow,

  // 백엔드
  nodejs: Server,
  'node.js': Server,
  express: Server,
  fastapi: Server,
  django: Server,
  flask: Server,
  api: Globe,
  'rest api': Globe,
  graphql: Globe,

  // 데이터베이스
  sql: Database,
  postgresql: Database,
  postgres: Database,
  mongodb: Database,
  redis: Database,
  mysql: Database,

  // 도구/인프라
  git: GitBranch,
  docker: Container,
  kubernetes: Boxes,
  k8s: Boxes,
  aws: Cloud,
  gcp: Cloud,
  azure: Cloud,

  // 테스팅
  testing: TestTube,
  jest: TestTube,
  vitest: TestTube,
  cypress: TestTube,

  // 배포
  deployment: Rocket,
  vercel: Rocket,
  netlify: Rocket,

  // 커리어
  portfolio: Briefcase,
  resume: FileText,
  interview: Users,

  // 기타
  python: Code2,
  java: Code2,
  package: Package,
  learning: GraduationCap,
  tutorial: BookOpen,
  video: Video,
};

// 플랫폼 -> 아이콘 매핑
const PLATFORM_ICON_MAP: Record<string, LucideIcon> = {
  YouTube: Video,
  Inflearn: GraduationCap,
  Nomad: GraduationCap,
  Official: BookOpen,
  MDN: BookOpen,
  Docs: BookOpen,
  GitHub: GitBranch,
};

export const TechIcon: React.FC<TechIconProps> = ({
  keyword,
  className = '',
  size = 20
}) => {
  // 키워드 정규화 (소문자, 공백 제거)
  const normalizedKeyword = keyword.toLowerCase().trim();

  // 아이콘 찾기
  const Icon = TECH_ICON_MAP[normalizedKeyword] || Code2; // 기본 아이콘

  return <Icon size={size} className={className} />;
};

export const PlatformIcon: React.FC<TechIconProps> = ({
  keyword,
  className = '',
  size = 16
}) => {
  const Icon = PLATFORM_ICON_MAP[keyword] || BookOpen; // 기본 아이콘

  return <Icon size={size} className={className} />;
};

// 다중 키워드 아이콘 표시 컴포넌트
interface TechIconGroupProps {
  keywords: string[];
  maxIcons?: number;
  className?: string;
}

export const TechIconGroup: React.FC<TechIconGroupProps> = ({
  keywords,
  maxIcons = 4,
  className = ''
}) => {
  const displayKeywords = keywords.slice(0, maxIcons);
  const remaining = keywords.length - maxIcons;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {displayKeywords.map((keyword, index) => (
        <div
          key={index}
          className="flex items-center gap-1 rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-700 dark:bg-blue-900 dark:text-blue-300"
          title={keyword}
        >
          <TechIcon keyword={keyword} size={14} />
          <span className="font-medium">{keyword}</span>
        </div>
      ))}
      {remaining > 0 && (
        <span className="text-xs text-gray-500">+{remaining}</span>
      )}
    </div>
  );
};

export default TechIcon;
