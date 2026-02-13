/**
 * FeedbackSection Component - AI 피드백 시각화
 * Strengths, Weaknesses, Potential, Action Items
 */

import { motion } from 'framer-motion';
import { getKoreanLabel } from '@/utils/labelMapper';
import { FeedbackCard } from './FeedbackCard';
import { sectionConfig, isString } from './feedbackConfig';
import type { FeedbackItem } from './feedbackConfig';

interface FeedbackSectionProps {
  summary?: string;
  strengths?: FeedbackItem[] | string[];
  weaknesses?: FeedbackItem[] | string[];
  improvements?: FeedbackItem[] | string[];
  potential?: FeedbackItem[] | string[];
  actionItems?: string[];
}

// 텍스트 내의 작은따옴표로 감싸진 영문 키워드를 한글로 변환
const translateKeywordsInText = (text: string): string =>
  text.replace(/'([^']+)'/g, (match, keyword) => {
    const koreanLabel = getKoreanLabel(keyword);
    if (koreanLabel !== keyword && koreanLabel.toLowerCase() !== keyword.toLowerCase()) {
      return `'${koreanLabel}'`;
    }
    return match;
  });

// 유효한 항목인지 체크하는 헬퍼
const isValidItem = (item: unknown): boolean => {
  if (!item) return false;
  if (isString(item)) return item.trim().length > 0;
  const obj = item as FeedbackItem;
  return typeof obj.description === 'string' && obj.description.trim().length > 0;
};

// 배열에서 유효한 항목만 필터링하고 영문 키워드를 한글로 변환
const filterValidItems = (items?: (FeedbackItem | string)[]): (FeedbackItem | string)[] => {
  if (!items || !Array.isArray(items)) return [];

  return items.filter(isValidItem).map((item) => {
    if (isString(item)) {
      return translateKeywordsInText(item);
    }
    return {
      ...item,
      title: item.title ? translateKeywordsInText(item.title) : item.title,
      description: translateKeywordsInText(item.description),
      category: item.category ? getKoreanLabel(item.category) : item.category,
    };
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
  const filteredStrengths = filterValidItems(strengths);
  const filteredWeaknesses = filterValidItems(weaknesses || improvements);
  const filteredPotential = filterValidItems(potential);
  const filteredActionItems = filterValidItems(actionItems);
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

export default FeedbackSection;
