import { clsx } from 'clsx';

interface UploadProgressStepsProps {
  resumeFile: File | null;
  jdFile: File | null;
  isAnalysisEnabled: boolean;
}

export const UploadProgressSteps: React.FC<UploadProgressStepsProps> = ({
  resumeFile,
  jdFile,
  isAnalysisEnabled,
}) => (
  <div className="flex items-center space-x-3 text-sm">
    <div
      className={clsx(
        'flex h-9 w-9 items-center justify-center rounded-full border-2 font-medium transition-all duration-200',
        {
          'border-emerald-500/50 bg-emerald-500/10 text-emerald-400': resumeFile,
          'border-slate-700 bg-slate-800/50 text-slate-500': !resumeFile,
        }
      )}
    >
      {resumeFile ? '✓' : '1'}
    </div>
    <span className="text-sm text-slate-400">이력서</span>

    <div className="h-px w-12 bg-slate-700" />

    <div
      className={clsx(
        'flex h-9 w-9 items-center justify-center rounded-full border-2 font-medium transition-all duration-200',
        {
          'border-emerald-500/50 bg-emerald-500/10 text-emerald-400': jdFile,
          'border-slate-700 bg-slate-800/50 text-slate-500': !jdFile,
        }
      )}
    >
      {jdFile ? '✓' : '2'}
    </div>
    <span className="text-sm text-slate-400">채용 공고</span>

    <div className="h-px w-12 bg-slate-700" />

    <div
      className={clsx(
        'flex h-9 w-9 items-center justify-center rounded-full border-2 font-medium transition-all duration-200',
        {
          'border-blue-500/50 bg-blue-500/10 text-blue-400': isAnalysisEnabled,
          'border-slate-700 bg-slate-800/50 text-slate-500': !isAnalysisEnabled,
        }
      )}
    >
      3
    </div>
    <span className="text-sm text-slate-400">분석</span>
  </div>
);

export default UploadProgressSteps;
