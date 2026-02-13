/**
 * StatCard - 통계 정보 카드 공통 컴포넌트
 *
 * AnalysisPage (color 없음, slate 스타일) 와
 * ResultPage (color 있음, 컬러 스타일 + 애니메이션) 에서 공통으로 사용
 */

import { motion } from 'framer-motion';

type StatCardColor = 'blue' | 'green' | 'purple' | 'orange';

interface StatCardProps {
  label: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  /** 제공하지 않으면 slate 정적 스타일, 제공하면 컬러 동적 스타일 + 애니메이션 */
  color?: StatCardColor;
}

const colorClasses: Record<StatCardColor, { icon: string; bg: string; border: string }> = {
  blue: {
    icon: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
  },
  green: {
    icon: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
  },
  purple: {
    icon: 'text-purple-400',
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
  },
  orange: {
    icon: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
  },
};

export const StatCard: React.FC<StatCardProps> = ({ label, value, subtitle, icon, color }) => {
  if (color) {
    const colors = colorClasses[color];
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className={`rounded-xl border backdrop-blur-sm ${colors.border} ${colors.bg}`}
      >
        <div className="flex items-center justify-between p-4">
          <div className="flex-1">
            <p className="text-xs font-medium text-slate-500">{label}</p>
            <p className="mt-1 text-2xl font-bold text-slate-100">{value}</p>
            {subtitle && <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>}
          </div>
          <div className={colors.icon}>{icon}</div>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800/50 bg-slate-900/30 p-4 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium text-slate-500">{label}</p>
          <p className="mt-1 text-lg font-semibold text-slate-100">{value}</p>
          {subtitle && <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>}
        </div>
        <div className="text-slate-500">{icon}</div>
      </div>
    </div>
  );
};

export default StatCard;
