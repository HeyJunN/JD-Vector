import { clsx } from 'clsx';
import type { UploadResponseData } from '@/lib/api';

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ children, className }) => (
  <span
    className={clsx(
      'inline-flex items-center rounded-full px-3 py-1 text-xs font-medium',
      className
    )}
  >
    {children}
  </span>
);

export interface DocumentPanelProps {
  title: string;
  filename: string;
  data: UploadResponseData;
  accentColor: 'emerald' | 'blue';
}

const accentClasses = {
  emerald: {
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/5',
    text: 'text-emerald-400',
    badge: 'bg-emerald-500/10 text-emerald-400',
  },
  blue: {
    border: 'border-blue-500/30',
    bg: 'bg-blue-500/5',
    text: 'text-blue-400',
    badge: 'bg-blue-500/10 text-blue-400',
  },
};

export const DocumentPanel: React.FC<DocumentPanelProps> = ({
  title,
  filename,
  data,
  accentColor,
}) => {
  const colors = accentClasses[accentColor];

  return (
    <div
      className={clsx(
        'rounded-xl border-2 backdrop-blur-sm',
        colors.border,
        colors.bg
      )}
    >
      {/* Header - 반응형 */}
      <div className="border-b border-slate-800/50 p-4 sm:p-6">
        <h2 className={clsx('text-lg font-bold tracking-tight sm:text-xl', colors.text)}>
          {title}
        </h2>
        <p className="mt-2 truncate text-xs text-slate-400 sm:text-sm">{filename}</p>

        {/* Metadata Badges - 반응형 */}
        <div className="mt-3 flex flex-wrap gap-1.5 sm:mt-4 sm:gap-2">
          <Badge className={colors.badge}>{data.metadata.page_count} 페이지</Badge>
          <Badge className={colors.badge}>{data.word_count.toLocaleString()} 단어</Badge>
          <Badge className={colors.badge}>{data.char_count.toLocaleString()} 자</Badge>
          <Badge className={colors.badge}>언어: {data.metadata.language.toUpperCase()}</Badge>
          <Badge className={colors.badge}>파서: {data.metadata.parser_used}</Badge>
        </div>
      </div>

      {/* Content - 반응형 */}
      <div className="p-4 sm:p-6">
        <div className="relative">
          {/* Scrollable Text Area - 반응형 높이 */}
          <div className="max-h-[400px] overflow-y-auto rounded-lg border border-slate-800/50 bg-slate-900/50 p-4 md:max-h-[500px] md:p-6 lg:max-h-[600px]">
            <pre className="whitespace-pre-wrap break-words font-mono text-xs leading-relaxed text-slate-300 sm:text-sm">
              {data.cleaned_text}
            </pre>
          </div>

          {/* Scroll Fade Indicator */}
          <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-slate-900/80 to-transparent" />
        </div>

        {/* Text Stats - 반응형 */}
        <div className="mt-4 flex flex-col items-start justify-between gap-1 text-xs text-slate-500 sm:flex-row sm:items-center">
          <span>텍스트 길이: {data.cleaned_text.length.toLocaleString()} 자</span>
          <span>처리 시간: {data.metadata.extraction_time_ms}ms</span>
        </div>
      </div>
    </div>
  );
};

export default DocumentPanel;
