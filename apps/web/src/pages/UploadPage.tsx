import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileUpload } from '@/components/upload/FileUpload';
import { ArrowRight, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

export const UploadPage = () => {
  const navigate = useNavigate();
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);

  const isAnalysisEnabled = resumeFile !== null && jdFile !== null;

  const handleAnalyze = () => {
    if (!isAnalysisEnabled) return;

    // TODO: Pass files data to analysis page
    // For now, just navigate
    navigate('/analysis', {
      state: {
        resumeFile,
        jdFile,
      },
    });
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-20">
        {/* Upload Grid - Now the main focus */}
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
          {/* Resume Upload */}
          <div className="flex flex-col">
            <FileUpload
              fileType="resume"
              onFileSelect={setResumeFile}
              maxSize={10 * 1024 * 1024} // 10MB
            />
          </div>

          {/* JD Upload */}
          <div className="flex flex-col">
            <FileUpload
              fileType="jd"
              onFileSelect={setJdFile}
              maxSize={10 * 1024 * 1024} // 10MB
            />
          </div>
        </div>

        {/* Action Section */}
        <div className="mt-12 flex flex-col items-center justify-center space-y-8 lg:mt-16">
          {/* Progress Indicator */}
          <div className="flex items-center space-x-3 text-sm">
            <div
              className={clsx(
                'flex h-9 w-9 items-center justify-center rounded-full border-2 font-medium transition-all duration-200',
                {
                  'border-emerald-500/50 bg-emerald-500/10 text-emerald-400':
                    resumeFile,
                  'border-slate-700 bg-slate-800/50 text-slate-500':
                    !resumeFile,
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
                  'border-emerald-500/50 bg-emerald-500/10 text-emerald-400':
                    jdFile,
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
                  'border-blue-500/50 bg-blue-500/10 text-blue-400':
                    isAnalysisEnabled,
                  'border-slate-700 bg-slate-800/50 text-slate-500':
                    !isAnalysisEnabled,
                }
              )}
            >
              3
            </div>
            <span className="text-sm text-slate-400">분석</span>
          </div>

          {/* Analyze Button - Minimal Sophistication Style */}
          <button
            onClick={handleAnalyze}
            disabled={!isAnalysisEnabled}
            className={clsx(
              'group relative inline-flex items-center space-x-3 rounded-xl border px-8 py-4 text-base font-semibold shadow-lg transition-all duration-200',
              {
                // Enabled state - White button on dark background
                'border-slate-200 bg-slate-50 text-slate-950 shadow-slate-50/10 hover:scale-[1.02] hover:border-white hover:bg-white hover:shadow-slate-50/20 hover:shadow-xl active:scale-[0.98]':
                  isAnalysisEnabled,
                // Disabled state
                'cursor-not-allowed border-slate-800 bg-slate-900/50 text-slate-600 opacity-60':
                  !isAnalysisEnabled,
              }
            )}
          >
            <Sparkles className="h-5 w-5" />
            <span>AI 분석 시작하기</span>
            <ArrowRight
              className={clsx('h-5 w-5 transition-transform duration-200', {
                'group-hover:translate-x-1': isAnalysisEnabled,
              })}
            />

            {/* Subtle outer glow on hover (enabled only) */}
            {isAnalysisEnabled && (
              <div className="absolute inset-0 -z-10 rounded-xl bg-slate-50/20 opacity-0 blur-xl transition-opacity duration-200 group-hover:opacity-100" />
            )}
          </button>

          {/* Helper Text */}
          {!isAnalysisEnabled && (
            <p className="text-sm text-slate-500">
              두 파일을 모두 업로드해야 분석을 시작할 수 있습니다
            </p>
          )}
        </div>

        {/* Info Cards */}
        <div className="mt-16 grid gap-8 sm:grid-cols-3 lg:mt-24">
          <div className="group rounded-xl border border-slate-800/50 bg-slate-900/30 p-8 backdrop-blur-sm transition-all duration-200 hover:border-slate-700 hover:bg-slate-900/50">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 transition-colors group-hover:bg-blue-500/20">
              <span className="text-3xl">📊</span>
            </div>
            <h3 className="mb-3 text-lg font-semibold tracking-tight text-slate-100">
              역량 분석
            </h3>
            <p className="text-sm leading-relaxed text-slate-400">
              AI가 귀하의 기술 스택과 JD 요구사항 간의 매칭도를 정밀하게
              분석합니다
            </p>
          </div>

          <div className="group rounded-xl border border-slate-800/50 bg-slate-900/30 p-8 backdrop-blur-sm transition-all duration-200 hover:border-slate-700 hover:bg-slate-900/50">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 transition-colors group-hover:bg-purple-500/20">
              <span className="text-3xl">🎯</span>
            </div>
            <h3 className="mb-3 text-lg font-semibold tracking-tight text-slate-100">
              간극 파악
            </h3>
            <p className="text-sm leading-relaxed text-slate-400">
              부족한 역량을 시각화하여 명확하게 파악할 수 있습니다
            </p>
          </div>

          <div className="group rounded-xl border border-slate-800/50 bg-slate-900/30 p-8 backdrop-blur-sm transition-all duration-200 hover:border-slate-700 hover:bg-slate-900/50">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 transition-colors group-hover:bg-emerald-500/20">
              <span className="text-3xl">🗺️</span>
            </div>
            <h3 className="mb-3 text-lg font-semibold tracking-tight text-slate-100">
              로드맵 제공
            </h3>
            <p className="text-sm leading-relaxed text-slate-400">
              맞춤형 학습 로드맵과 실행 가능한 액션 플랜을 제안합니다
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
