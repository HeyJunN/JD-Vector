import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { FileUpload } from '@/components/upload/FileUpload';
import { UploadLoadingOverlay } from '@/components/upload/UploadLoadingOverlay';
import { UploadProgressSteps } from '@/components/upload/UploadProgressSteps';
import { ArrowRight, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';
import { uploadResume, uploadJobDescription } from '@/lib/api';
import { analysisService } from '@/services/analysisService';

export const UploadPage = () => {
  const navigate = useNavigate();
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);

  // 업로드 상태 관리
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStage, setUploadStage] = useState<string>('');

  const isAnalysisEnabled = resumeFile !== null && jdFile !== null && !isUploading;

  /**
   * 파일 업로드 및 분석 시작
   * 순차적으로 이력서 -> JD 업로드 후 /analysis 페이지로 이동
   */
  const handleAnalyze = async () => {
    if (!isAnalysisEnabled || !resumeFile || !jdFile) return;

    setIsUploading(true);
    let toastId: string | undefined;

    try {
      // 1. 이력서 업로드
      setUploadStage('이력서를 업로드하고 있습니다...');
      toastId = toast.loading('이력서를 업로드하고 있습니다...');

      const resumeResponse = await uploadResume(resumeFile);

      toast.dismiss(toastId);
      toast.success(
        `이력서 업로드 완료 (${resumeResponse.metadata.page_count}페이지, ${resumeResponse.word_count.toLocaleString()}단어)`
      );

      // 개발 환경에서 cleaned_text 로깅
      if (import.meta.env.DEV) {
        console.log('[Resume Upload Success]', {
          file_id: resumeResponse.file_id,
          filename: resumeResponse.filename,
          word_count: resumeResponse.word_count,
          char_count: resumeResponse.char_count,
          page_count: resumeResponse.metadata.page_count,
          language: resumeResponse.metadata.language,
          parser: resumeResponse.metadata.parser_used,
          cleaned_text_preview: resumeResponse.cleaned_text.substring(0, 200) + '...',
        });
      }

      // 2. 채용 공고 업로드
      setUploadStage('AI가 채용 공고를 분석하고 있습니다...');
      toastId = toast.loading('AI가 채용 공고를 분석하고 있습니다...');

      const jdResponse = await uploadJobDescription(jdFile);

      toast.dismiss(toastId);
      toast.success(
        `채용 공고 분석 완료 (${jdResponse.metadata.page_count}페이지, ${jdResponse.word_count.toLocaleString()}단어)`
      );

      // 개발 환경에서 cleaned_text 로깅
      if (import.meta.env.DEV) {
        console.log('[JD Upload Success]', {
          file_id: jdResponse.file_id,
          filename: jdResponse.filename,
          word_count: jdResponse.word_count,
          char_count: jdResponse.char_count,
          page_count: jdResponse.metadata.page_count,
          language: jdResponse.metadata.language,
          parser: jdResponse.metadata.parser_used,
          cleaned_text_preview: jdResponse.cleaned_text.substring(0, 200) + '...',
        });
      }

      // 3. 벡터화 완료 확인 (서버에서 동기식으로 처리되므로 즉시 조회 가능)
      setUploadStage('벡터화 상태를 확인하는 중...');
      toastId = toast.loading('벡터화 상태를 확인하는 중...');

      const [resumeStatus, jdStatus] = await Promise.all([
        analysisService.getDocumentStatus(resumeResponse.file_id),
        analysisService.getDocumentStatus(jdResponse.file_id),
      ]);

      if (resumeStatus.embedding_status !== 'completed') {
        throw new Error(
          `이력서 임베딩에 실패했습니다 (상태: ${resumeStatus.embedding_status ?? '알 수 없음'}). 잠시 후 다시 시도해주세요.`
        );
      }
      if (jdStatus.embedding_status !== 'completed') {
        throw new Error(
          `채용공고 임베딩에 실패했습니다 (상태: ${jdStatus.embedding_status ?? '알 수 없음'}). 잠시 후 다시 시도해주세요.`
        );
      }

      toast.dismiss(toastId);
      toast.success('벡터화가 완료되었습니다!');

      // 4. 성공 - 분석 페이지로 이동
      toast.success('파일 업로드가 완료되었습니다! 분석을 시작합니다.');

      // React Router state로 데이터 전달 (URL 파라미터보다 안전)
      navigate('/analysis', {
        state: {
          resumeData: resumeResponse,
          jdData: jdResponse,
        },
      });
    } catch (error) {
      // 에러 처리
      if (toastId) {
        toast.dismiss(toastId);
      }

      const errorMessage =
        error instanceof Error ? error.message : '파일 업로드 중 오류가 발생했습니다.';

      toast.error(errorMessage);

      // 개발 환경에서 상세 에러 로깅
      if (import.meta.env.DEV) {
        console.error('[Upload Error]', error);
      }
    } finally {
      setIsUploading(false);
      setUploadStage('');
    }
  };

  return (
    <div className="relative min-h-screen bg-slate-950">
      {/* Loading Overlay - 업로드 중일 때만 표시 */}
      <UploadLoadingOverlay isVisible={isUploading} message={uploadStage} />

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
          <UploadProgressSteps
            resumeFile={resumeFile}
            jdFile={jdFile}
            isAnalysisEnabled={isAnalysisEnabled}
          />

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
