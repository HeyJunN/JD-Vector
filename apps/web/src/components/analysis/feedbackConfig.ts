import {
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Target,
} from 'lucide-react';

export interface FeedbackItem {
  title?: string;
  description: string;
  score?: number;
  category?: string;
}

export const sectionConfig = {
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

export const isString = (item: unknown): item is string => typeof item === 'string';
