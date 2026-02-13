import { motion } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';
import { sectionConfig, isString } from './feedbackConfig';
import type { FeedbackItem } from './feedbackConfig';

export interface FeedbackCardProps {
  type: keyof typeof sectionConfig;
  items: (FeedbackItem | string)[];
  delay?: number;
}

export const FeedbackCard: React.FC<FeedbackCardProps> = ({ type, items, delay = 0 }) => {
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

export default FeedbackCard;
