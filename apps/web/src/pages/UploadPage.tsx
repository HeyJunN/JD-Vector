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
      {/* Header Section */}
      <div className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white sm:text-4xl">
              파일 업로드
            </h1>
            <p className="mt-2 text-base text-gray-400 sm:text-lg">
              이력서와 채용 공고를 업로드하여 AI 기반 적합도 분석을 시작하세요
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        {/* Upload Grid */}
        <div className="grid gap-8 lg:grid-cols-2">
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
        <div className="mt-12 flex flex-col items-center justify-center space-y-6">
          {/* Progress Indicator */}
          <div className="flex items-center space-x-2 text-sm">
            <div
              className={clsx(
                'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all duration-200',
                {
                  'border-green-500 bg-green-500/20 text-green-400':
                    resumeFile,
                  'border-gray-700 bg-gray-800 text-gray-500': !resumeFile,
                }
              )}
            >
              {resumeFile ? '✓' : '1'}
            </div>
            <span className="text-gray-400">이력서</span>

            <div className="h-px w-8 bg-gray-700" />

            <div
              className={clsx(
                'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all duration-200',
                {
                  'border-green-500 bg-green-500/20 text-green-400': jdFile,
                  'border-gray-700 bg-gray-800 text-gray-500': !jdFile,
                }
              )}
            >
              {jdFile ? '✓' : '2'}
            </div>
            <span className="text-gray-400">채용 공고</span>

            <div className="h-px w-8 bg-gray-700" />

            <div
              className={clsx(
                'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all duration-200',
                {
                  'border-blue-500 bg-blue-500/20 text-blue-400':
                    isAnalysisEnabled,
                  'border-gray-700 bg-gray-800 text-gray-500':
                    !isAnalysisEnabled,
                }
              )}
            >
              3
            </div>
            <span className="text-gray-400">분석</span>
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={!isAnalysisEnabled}
            className={clsx(
              'group relative inline-flex items-center space-x-2 rounded-lg px-8 py-4 text-base font-semibold transition-all duration-200',
              {
                // Enabled state
                'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/50 hover:shadow-xl hover:shadow-blue-500/60 hover:scale-105':
                  isAnalysisEnabled,
                // Disabled state
                'cursor-not-allowed bg-gray-800 text-gray-500 opacity-50':
                  !isAnalysisEnabled,
              }
            )}
          >
            <Sparkles className="h-5 w-5" />
            <span>AI 분석 시작하기</span>
            <ArrowRight
              className={clsx('h-5 w-5 transition-transform', {
                'group-hover:translate-x-1': isAnalysisEnabled,
              })}
            />
          </button>

          {/* Helper Text */}
          {!isAnalysisEnabled && (
            <p className="text-sm text-gray-500">
              두 파일을 모두 업로드해야 분석을 시작할 수 있습니다
            </p>
          )}
        </div>

        {/* Info Cards */}
        <div className="mt-16 grid gap-6 sm:grid-cols-3">
          <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="mb-2 font-semibold text-white">역량 분석</h3>
            <p className="text-sm text-gray-400">
              AI가 귀하의 기술 스택과 JD 요구사항 간의 매칭도를 분석합니다
            </p>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/10">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="mb-2 font-semibold text-white">간극 파악</h3>
            <p className="text-sm text-gray-400">
              부족한 역량을 시각화하여 명확하게 보여드립니다
            </p>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10">
              <span className="text-2xl">🗺️</span>
            </div>
            <h3 className="mb-2 font-semibold text-white">로드맵 제공</h3>
            <p className="text-sm text-gray-400">
              맞춤형 학습 로드맵과 실행 가능한 액션 플랜을 제안합니다
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
