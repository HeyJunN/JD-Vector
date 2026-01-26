/**
 * FeedbackSection Component - AI 피드백 시각화
 * Strengths, Weaknesses, Potential, Action Items
 */

import { motion } from 'framer-motion';
import {
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Target,
  ChevronRight,
} from 'lucide-react';
import { clsx } from 'clsx';
import { getKoreanLabel } from '@/utils/labelMapper';

interface FeedbackItem {
  title?: string;
  description: string;
  score?: number;
  category?: string;
}

interface FeedbackSectionProps {
  summary?: string;
  strengths?: FeedbackItem[] | string[];
  weaknesses?: FeedbackItem[] | string[];
  improvements?: FeedbackItem[] | string[];
  potential?: FeedbackItem[] | string[];
  actionItems?: string[];
}

// 섹션 설정
const sectionConfig = {
  strengths: {
    title: '강점',
    icon: CheckCircle2,
    iconColor: 'text-green-400',
    bgColor: 'bg-green-500/5',
    borderColor: 'border-green-500/30',
    badgeColor: 'bg-green-500/10 text-green-400',
  },
  weaknesses: {
    title: '개선점',
    icon: AlertTriangle,
    iconColor: 'text-orange-400',
    bgColor: 'bg-orange-500/5',
    borderColor: 'border-orange-500/30',
    badgeColor: 'bg-orange-500/10 text-orange-400',
  },
  improvements: {
    title: '개선점',
    icon: AlertTriangle,
    iconColor: 'text-orange-400',
    bgColor: 'bg-orange-500/5',
    borderColor: 'border-orange-500/30',
    badgeColor: 'bg-orange-500/10 text-orange-400',
  },
  potential: {
    title: '잠재력',
    icon: Sparkles,
    iconColor: 'text-purple-400',
    bgColor: 'bg-purple-500/5',
    borderColor: 'border-purple-500/30',
    badgeColor: 'bg-purple-500/10 text-purple-400',
  },
  actionItems: {
    title: '실행 계획',
    icon: Target,
    iconColor: 'text-blue-400',
    bgColor: 'bg-blue-500/5',
    borderColor: 'border-blue-500/30',
    badgeColor: 'bg-blue-500/10 text-blue-400',
  },
};

// 문자열인지 객체인지 판단하는 헬퍼
const isString = (item: any): item is string => typeof item === 'string';

// 텍스트 내의 작은따옴표로 감싸진 영문 키워드를 한글로 변환
const translateKeywordsInText = (text: string): string => {
  // 작은따옴표로 감싸진 영문 키워드를 찾는 정규식
  // 예: 'preferred', 'requirements', 'technical' 등
  return text.replace(/'([^']+)'/g, (match, keyword) => {
    const koreanLabel = getKoreanLabel(keyword);
    // 원본이 영문이고 변환된 결과가 다르면 한글로 치환
    if (koreanLabel !== keyword && koreanLabel.toLowerCase() !== keyword.toLowerCase()) {
      return `'${koreanLabel}'`;
    }
    return match; // 변환할 수 없으면 원본 유지
  });
};

// 유효한 항목인지 체크하는 헬퍼
const isValidItem = (item: any): boolean => {
  if (!item) return false;

  if (isString(item)) {
    // 문자열인 경우 빈 문자열이 아니어야 함
    return item.trim().length > 0;
  }

  // 객체인 경우 description이 있고 비어있지 않아야 함
  return item.description && typeof item.description === 'string' && item.description.trim().length > 0;
};

// 배열에서 유효한 항목만 필터링하고 영문 키워드를 한글로 변환
const filterValidItems = (items?: (FeedbackItem | string)[]): (FeedbackItem | string)[] => {
  if (!items || !Array.isArray(items)) return [];

  return items
    .filter(isValidItem)
    .map((item) => {
      if (isString(item)) {
        // 문자열인 경우 키워드 변환
        return translateKeywordsInText(item);
      } else {
        // 객체인 경우 description과 title 변환
        return {
          ...item,
          title: item.title ? translateKeywordsInText(item.title) : item.title,
          description: translateKeywordsInText(item.description),
          category: item.category ? getKoreanLabel(item.category) : item.category,
        };
      }
    });
};

export const FeedbackSection: React.FC<FeedbackSectionProps> = ({
  summary,
  strengths,
  weaknesses,
  improvements,
  potential,
  actionItems,
}) => {
  // 모든 데이터를 필터링하여 유효한 항목만 남김
  const filteredStrengths = filterValidItems(strengths);
  const filteredWeaknesses = filterValidItems(weaknesses || improvements);
  const filteredPotential = filterValidItems(potential);
  const filteredActionItems = filterValidItems(actionItems);

  // Summary도 영문 키워드 변환
  const translatedSummary = summary ? translateKeywordsInText(summary) : '';

  const sections = [
    { key: 'strengths', data: filteredStrengths },
    { key: 'weaknesses', data: filteredWeaknesses },
    { key: 'potential', data: filteredPotential },
    { key: 'actionItems', data: filteredActionItems },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.4 }}
      className="space-y-6"
    >
      {/* Summary */}
      {translatedSummary && translatedSummary.trim().length > 0 && (
        <div className="rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-6 backdrop-blur-sm">
          <h3 className="mb-3 text-xl font-bold text-slate-100">AI 종합 분석</h3>
          <p className="leading-relaxed text-slate-300">{translatedSummary}</p>
        </div>
      )}

      {/* Feedback Sections */}
      <div className="grid gap-6 lg:grid-cols-2">
        {sections.map(
          ({ key, data }, index) =>
            data &&
            data.length > 0 && (
              <FeedbackCard
                key={key}
                type={key as keyof typeof sectionConfig}
                items={data}
                delay={index * 0.1}
              />
            )
        )}
      </div>
    </motion.div>
  );
};

interface FeedbackCardProps {
  type: keyof typeof sectionConfig;
  items: (FeedbackItem | string)[];
  delay?: number;
}

const FeedbackCard: React.FC<FeedbackCardProps> = ({ type, items, delay = 0 }) => {
  const config = sectionConfig[type];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={clsx(
        'rounded-2xl border backdrop-blur-sm',
        config.borderColor,
        config.bgColor
      )}
    >
      {/* Header */}
      <div className="border-b border-slate-800/50 p-5">
        <div className="flex items-center gap-3">
          <div className={clsx('rounded-lg p-2', config.badgeColor)}>
            <Icon className={clsx('h-5 w-5', config.iconColor)} />
          </div>
          <div>
            <h4 className="text-lg font-bold text-slate-100">{config.title}</h4>
            <p className="text-sm text-slate-400">{items.length}개 항목</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        <ul className="space-y-3">
          {items.map((item, idx) => (
            <motion.li
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: delay + idx * 0.05 }}
              className="flex items-start gap-3 rounded-lg border border-slate-800/30 bg-slate-900/50 p-3 transition-colors hover:border-slate-700/50 hover:bg-slate-900/70"
            >
              <ChevronRight
                className={clsx('mt-0.5 h-4 w-4 flex-shrink-0', config.iconColor)}
              />
              <div className="flex-1 space-y-1">
                {isString(item) ? (
                  <p className="text-sm leading-relaxed text-slate-300">{item}</p>
                ) : (
                  <>
                    {item.title && (
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-slate-200">{item.title}</p>
                        {item.score !== undefined && (
                          <span className={clsx('text-xs font-medium', config.badgeColor, 'rounded-full px-2 py-0.5')}>
                            {item.score}점
                          </span>
                        )}
                      </div>
                    )}
                    <p className="text-sm leading-relaxed text-slate-300">
                      {item.description}
                    </p>
                    {item.category && (
                      <span className="inline-block rounded-full bg-slate-800/50 px-2 py-0.5 text-xs text-slate-400">
                        {item.category}
                      </span>
                    )}
                  </>
                )}
              </div>
            </motion.li>
          ))}
        </ul>
      </div>
    </motion.div>
  );
};

export default FeedbackSection;
