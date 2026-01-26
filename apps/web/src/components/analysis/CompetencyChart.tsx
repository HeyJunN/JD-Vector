/**
 * CompetencyChart Component - Radar Chart로 역량 비교
 */

import { motion } from 'framer-motion';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { User, Briefcase } from 'lucide-react';
import { getKoreanLabel } from '@/utils/labelMapper';

interface CompetencyData {
  category: string;
  userScore: number; // 0-100
  jdRequirement: number; // 0-100
}

interface CompetencyChartProps {
  data: CompetencyData[];
  title?: string;
}

// Custom Tooltip
const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload || !payload.length) return null;

  // 원본 영문 키를 한글로 변환
  const koreanLabel = getKoreanLabel(payload[0].payload.originalCategory || payload[0].payload.category);

  // Radar 순서: [0] = jdRequirement (목표 수준), [1] = userScore (현재 매칭도)
  const jdRequirementValue = payload[0]?.value || 0;
  const userScoreValue = payload[1]?.value || 0;

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900/95 p-3 shadow-xl backdrop-blur-sm">
      <p className="mb-2 font-semibold text-slate-200">{koreanLabel}</p>
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-sm">
          <div className="h-3 w-3 rounded-full bg-emerald-400" />
          <span className="text-slate-300">현재 매칭도:</span>
          <span className="font-semibold text-emerald-400">{userScoreValue}점</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <div className="h-3 w-3 rounded-full bg-blue-400" />
          <span className="text-slate-300">목표 수준:</span>
          <span className="font-semibold text-blue-400">{jdRequirementValue}점</span>
        </div>
        {userScoreValue < jdRequirementValue && (
          <div className="mt-2 rounded bg-orange-500/10 px-2 py-1 text-xs text-orange-400">
            <span className="font-medium">
              향상 목표: {jdRequirementValue - userScoreValue}점
            </span>
          </div>
        )}
        {userScoreValue >= jdRequirementValue && (
          <div className="mt-2 rounded bg-emerald-500/10 px-2 py-1 text-xs text-emerald-400">
            <span className="font-medium">
              ✓ 목표 달성!
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export const CompetencyChart: React.FC<CompetencyChartProps> = ({
  data,
  title = '역량 비교 분석'
}) => {
  // 데이터 정규화 + 한글 레이블 변환
  const normalizedData = data.map((item) => {
    const originalCategory = item.category || 'Unknown';
    const koreanCategory = getKoreanLabel(originalCategory);

    return {
      category: koreanCategory, // 차트에 표시될 한글 레이블
      originalCategory, // 원본 영문 키 보존 (디버깅/참조용)
      userScore: Math.max(0, Math.min(100, Math.round(item.userScore || 0))),
      jdRequirement: Math.max(0, Math.min(100, Math.round(item.jdRequirement || 0))),
    };
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-6 backdrop-blur-sm md:p-8"
    >
      {/* Header */}
      <div className="mb-6">
        <h3 className="mb-2 text-xl font-bold text-slate-100 md:text-2xl">{title}</h3>
        <p className="text-sm text-slate-400 md:text-base">
          각 역량 영역별 매칭도를 비교합니다. 파란 영역이 목표, 초록 영역이 현재 수준입니다.
        </p>
      </div>

      {/* Chart */}
      <div className="relative">
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={normalizedData}>
            <PolarGrid stroke="#334155" strokeWidth={1} />
            <PolarAngleAxis
              dataKey="category"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              tickLine={false}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              allowDataOverflow={false}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickCount={6}
              ticks={[0, 20, 40, 60, 80, 100]}
            />

            {/* 목표 수준 (파란색) - 먼저 렌더링하여 뒤에 배치 */}
            <Radar
              name="목표 수준"
              dataKey="jdRequirement"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.25}
              strokeWidth={2}
            />

            {/* 현재 매칭도 (초록색) - 나중에 렌더링하여 앞에 배치 */}
            <Radar
              name="현재 매칭도"
              dataKey="userScore"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.4}
              strokeWidth={2}
            />

            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                paddingTop: '20px',
              }}
              iconType="circle"
              formatter={(value: string) => (
                <span className="text-sm font-medium text-slate-300">{value}</span>
              )}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend Explanation */}
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="flex items-center gap-3 rounded-xl border border-slate-800/50 bg-emerald-500/5 p-3">
          <div className="rounded-lg bg-emerald-500/10 p-2">
            <User className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <div className="text-sm font-semibold text-emerald-400">현재 매칭도</div>
            <div className="text-xs text-slate-400">각 영역별 현재 점수</div>
          </div>
        </div>

        <div className="flex items-center gap-3 rounded-xl border border-slate-800/50 bg-blue-500/5 p-3">
          <div className="rounded-lg bg-blue-500/10 p-2">
            <Briefcase className="h-5 w-5 text-blue-400" />
          </div>
          <div>
            <div className="text-sm font-semibold text-blue-400">목표 수준</div>
            <div className="text-xs text-slate-400">채용 공고 충족 기준</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default CompetencyChart;
