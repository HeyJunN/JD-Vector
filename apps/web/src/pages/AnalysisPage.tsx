import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { CheckCircle2, FileText, ArrowRight, Sparkles, Loader2 } from 'lucide-react';
import type { UploadResponseData } from '@/lib/api';
import { analysisService } from '../services/analysisService';
import { StatCard } from '@/components/ui/StatCard';
import { DocumentPanel } from '@/components/analysis/DocumentPanel';

interface AnalysisPageState {
  resumeData: UploadResponseData;
  jdData: UploadResponseData;
}

export const AnalysisPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const state = location.state as AnalysisPageState | null;

  // 분석 로딩 상태
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // 데이터 유효성 검증 및 리다이렉트
  useEffect(() => {
    if (!state || !state.resumeData || !state.jdData) {
      // 사용자에게 친절한 알림 표시
      toast.error('업로드된 데이터가 없습니다. 파일을 먼저 업로드해주세요.');
      navigate('/upload', { replace: true });
    }
  }, [state, navigate]);

  // 데이터가 없으면 null 반환 (리다이렉트 처리 중)
  if (!state || !state.resumeData || !state.jdData) {
    return null;
  }

  const { resumeData, jdData } = state;

  // AI 분석 시작 핸들러
  const handleStartAnalysis = async () => {
    setIsAnalyzing(true);

    try {
      // 1. 이력서와 JD의 document_id 조회
      toast.loading('문서 벡터화 상태를 확인하는 중...', { id: 'check-status' });

      const [resumeDoc, jdDoc] = await Promise.all([
        analysisService.getDocumentStatus(resumeData.file_id),
        analysisService.getDocumentStatus(jdData.file_id),
      ]);

      // 2. 벡터화 완료 확인
      if (resumeDoc.embedding_status !== 'completed') {
        toast.error('이력서 벡터화가 아직 진행 중입니다. 잠시 후 다시 시도해주세요.', {
          id: 'check-status',
        });
        setIsAnalyzing(false);
        return;
      }

      if (jdDoc.embedding_status !== 'completed') {
        toast.error('채용공고 벡터화가 아직 진행 중입니다. 잠시 후 다시 시도해주세요.', {
          id: 'check-status',
        });
        setIsAnalyzing(false);
        return;
      }

      // 3. document_id 확인
      if (!resumeDoc.document_id || !jdDoc.document_id) {
        toast.error('문서 ID를 찾을 수 없습니다.', { id: 'check-status' });
        setIsAnalyzing(false);
        return;
      }

      toast.success('문서 준비 완료!', { id: 'check-status' });

      // 4. 매칭 분석 수행
      toast.loading('AI가 적합도를 분석하는 중...', { id: 'analysis' });

      const analysisResult = await analysisService.analyzeMatch({
        resume_id: resumeDoc.document_id,
        jd_id: jdDoc.document_id,
      });

      if (!analysisResult.success) {
        throw new Error(analysisResult.message || '분석에 실패했습니다.');
      }

      toast.success('분석 완료!', { id: 'analysis' });

      // 5. ResultPage로 이동 (분석 결과 시각화)
      navigate('/result', {
        state: {
          analysisResult: analysisResult.data,
        },
      });
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(
        error instanceof Error ? error.message : '분석 중 오류가 발생했습니다.',
        { id: 'analysis' }
      );
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header Section */}
      <div className="border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {/* Success Message - 반응형 */}
          <div className="mb-6 flex items-center space-x-3">
            <div className="flex-shrink-0 rounded-full bg-emerald-500/10 p-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-400 sm:h-6 sm:w-6" />
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-xl font-bold tracking-tight text-slate-100 sm:text-2xl">
                서류 분석 완료!
              </h1>
              <p className="mt-1 text-xs text-slate-400 sm:text-sm">
                이제 AI가 당신의 커리어를 매칭할 준비가 되었습니다
              </p>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="이력서"
              value={`${resumeData.metadata.page_count}페이지`}
              subtitle={`${resumeData.word_count.toLocaleString()}단어`}
              icon={<FileText className="h-5 w-5" />}
            />
            <StatCard
              label="채용 공고"
              value={`${jdData.metadata.page_count}페이지`}
              subtitle={`${jdData.word_count.toLocaleString()}단어`}
              icon={<FileText className="h-5 w-5" />}
            />
            <StatCard
              label="언어"
              value={resumeData.metadata.language.toUpperCase()}
              subtitle={`파서: ${resumeData.metadata.parser_used}`}
              icon={<Sparkles className="h-5 w-5" />}
            />
            <StatCard
              label="처리 시간"
              value={`${resumeData.metadata.extraction_time_ms + jdData.metadata.extraction_time_ms}ms`}
              subtitle="텍스트 추출 완료"
              icon={<CheckCircle2 className="h-5 w-5" />}
            />
          </div>
        </div>
      </div>

      {/* Main Content - Document Comparison */}
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Resume Section */}
          <DocumentPanel
            title="이력서"
            filename={resumeData.filename}
            data={resumeData}
            accentColor="emerald"
          />

          {/* JD Section */}
          <DocumentPanel
            title="채용 공고"
            filename={jdData.filename}
            data={jdData}
            accentColor="blue"
          />
        </div>

        {/* Next Step Button */}
        <div className="mt-12 flex flex-col items-center justify-center space-y-6">
          <div className="text-center">
            <p className="text-sm text-slate-400">
              업로드된 서류를 확인했다면 AI 적합도 분석을 시작하세요
            </p>
          </div>

          <button
            onClick={handleStartAnalysis}
            disabled={isAnalyzing}
            className="group relative inline-flex items-center space-x-3 rounded-xl border border-slate-200 bg-slate-50 px-8 py-4 text-base font-semibold text-slate-950 shadow-lg shadow-slate-50/10 transition-all duration-200 hover:scale-[1.02] hover:border-white hover:bg-white hover:shadow-xl hover:shadow-slate-50/20 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
          >
            {isAnalyzing ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Sparkles className="h-5 w-5" />
            )}
            <span>{isAnalyzing ? '분석 중...' : 'AI 적합도 분석 시작하기'}</span>
            {!isAnalyzing && (
              <ArrowRight className="h-5 w-5 transition-transform duration-200 group-hover:translate-x-1" />
            )}

            {/* Subtle outer glow on hover */}
            <div className="absolute inset-0 -z-10 rounded-xl bg-slate-50/20 opacity-0 blur-xl transition-opacity duration-200 group-hover:opacity-100" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
